import streamlit as st
import sqlite3
import pandas as pd
import time
import os
import altair as alt

DB_FILE = 'aiotdb.db'
SNAPSHOT_FILE = os.path.join('data', 'real_data.csv')
WINDOW = 100  # 畫面同時呈現的最新資料筆數

st.set_page_config(
    page_title="ESP32 戰情室",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入自訂動態漸層背景與質感 CSS (包含使用者指定色系)
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #2d232e, #474448, #534b52, #2d232e) !important;
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
div[data-testid="stMetricValue"] {
    color: #e0ddcf !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 ESP32 即時戰情室 (AIoT)")
st.markdown("實時監控 DHT11 溫濕度資料與連線狀態")


@st.cache_data
def load_snapshot():
    """載入封存的真實量測資料快照 (供雲端 / 離線 live demo 回放)。"""
    if not os.path.exists(SNAPSHOT_FILE):
        return pd.DataFrame()
    return pd.read_csv(SNAPSHOT_FILE)


def load_live_data():
    """本機模式：直接讀取 Flask API 即時寫入 SQLite 的最新 100 筆。"""
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(
            f"SELECT * FROM sensors ORDER BY timestamp DESC LIMIT {WINDOW}", conn
        )
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def get_frame():
    """
    自動切換資料來源：
      - 本機 (有 api.py 持續寫入 aiotdb.db)：回傳即時資料。
      - 雲端 Streamlit Cloud (無硬體/無 API)：回放封存的真實量測快照，
        以滑動視窗方式逐筆推進，讓 live demo 的曲線持續流動。
    回傳 (df, mode)；df 為時間升冪排序、最多 WINDOW 筆。
    """
    live = load_live_data()
    if not live.empty:
        return live.sort_values('timestamp'), "LIVE"

    snap = load_snapshot()
    if snap.empty:
        return snap, "EMPTY"

    # 以 session 計數器逐步推進播放指標，營造即時感
    st.session_state.setdefault("cursor", WINDOW)
    cursor = st.session_state["cursor"]
    if cursor >= len(snap):
        cursor = WINDOW
    frame = snap.iloc[max(0, cursor - WINDOW):cursor].copy()
    st.session_state["cursor"] = cursor + 1
    return frame, "REPLAY"


placeholder = st.empty()

while True:
    df, mode = get_frame()

    with placeholder.container():
        if not df.empty:
            latest = df.iloc[-1]

            # 與前一筆比對，計算指標卡的增減量 (delta)
            temp_delta = hum_delta = rssi_delta = None
            if len(df) > 1:
                prev = df.iloc[-2]
                temp_delta = f"{latest['temperature'] - prev['temperature']:.1f} °C"
                hum_delta = f"{latest['humidity'] - prev['humidity']:.1f} %"
                rssi_delta = f"{int(latest['wifi_rssi']) - int(prev['wifi_rssi'])} dBm"

            # 即時 KPI 指標卡
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🌡️ 最新溫度", f"{latest['temperature']} °C", temp_delta)
            col2.metric("💧 最新濕度", f"{latest['humidity']} %", hum_delta)
            col3.metric("📶 WiFi 訊號", f"{latest['wifi_rssi']} dBm", rssi_delta)

            update_time = str(latest['timestamp']).split('.')[0]
            update_time = update_time.split(' ')[1] if ' ' in update_time else update_time.split('T')[-1]
            col4.metric("⏱️ 最後更新", update_time)

            if mode == "REPLAY":
                st.caption("🟢 即時回放模式：來源為 ESP32 + DHT11 實機封存的真實量測資料 (`data/real_data.csv`)")
            elif mode == "LIVE":
                st.caption("🟢 即時連線模式：來源為本機 Flask API 寫入的 SQLite 資料庫")

            st.divider()

            # 整理繪圖資料：時間轉為 HH:MM:SS，並 melt 成長格式供雙線繪製
            df = df.copy()
            df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
            melted_df = df.melt(
                id_vars=['time'], value_vars=['temperature', 'humidity'],
                var_name='Metric', value_name='Value'
            )
            melted_df['Metric'] = melted_df['Metric'].map(
                {'temperature': '溫度 (°C)', 'humidity': '濕度 (%)'}
            )

            st.subheader("📈 溫濕度平滑趨勢圖")

            hover = alt.selection_point(fields=['time'], nearest=True, on='mouseover', empty=False)

            # 計算資料上下限並給予 20% 的延伸空間，避免折線貼齊邊緣
            min_val = melted_df['Value'].min()
            max_val = melted_df['Value'].max()
            padding = (max_val - min_val) * 0.2 if max_val != min_val else 5

            base_line = alt.Chart(melted_df).mark_line(
                interpolate='monotone', strokeWidth=3
            ).encode(
                x=alt.X('time:N', title='時間', axis=alt.Axis(labelAngle=-45, labelOverlap=True)),
                y=alt.Y('Value:Q', title='數值', scale=alt.Scale(domain=[min_val - padding, max_val + padding])),
                color=alt.Color('Metric:N',
                                scale=alt.Scale(domain=['溫度 (°C)', '濕度 (%)'], range=['#f1f0ea', '#4DD0E1']),
                                legend=alt.Legend(title="指標", orient='bottom'))
            )

            points = base_line.mark_point(size=80, filled=True).encode(
                opacity=alt.condition(hover, alt.value(1), alt.value(0)),
                tooltip=['time', 'Metric', 'Value']
            )

            rule = alt.Chart(melted_df).mark_rule(color='#e0ddcf', strokeDash=[4, 4]).encode(
                x='time:N',
                opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
                tooltip=['time', 'Metric', 'Value']
            ).add_params(hover)

            smooth_chart = alt.layer(base_line, rule, points).properties(height=450).interactive()
            st.altair_chart(smooth_chart, use_container_width=True)

            with st.expander("🔍 檢視近期歷史數據表格"):
                st.dataframe(df.iloc[::-1], use_container_width=True)
        else:
            st.warning("⏳ 正在等待 ESP32 感測器資料庫寫入...")

    time.sleep(2)
