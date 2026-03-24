import streamlit as st
import sqlite3
import pandas as pd
import time
import os
import altair as alt

DB_FILE = 'aiotdb.db'

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
st.markdown("實時監控溫濕度資料與連線狀態")

def load_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        if not df.empty:
            latest = df.iloc[0]
            
            # Form calculations for deltas
            temp_delta = hum_delta = rssi_delta = None
            if len(df) > 1:
                prev = df.iloc[1]
                temp_delta = f"{latest['temperature'] - prev['temperature']:.1f} °C"
                hum_delta = f"{latest['humidity'] - prev['humidity']:.1f} %"
                rssi_delta = f"{int(latest['wifi_rssi']) - int(prev['wifi_rssi'])} dBm"
                
            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🌡️ 最新溫度", f"{latest['temperature']} °C", temp_delta)
            col2.metric("💧 最新濕度", f"{latest['humidity']} %", hum_delta)
            col3.metric("📶 WiFi 訊號", f"{latest['wifi_rssi']} dBm", rssi_delta)
            
            # Format display time
            update_time = str(latest['timestamp']).split('.')[0].split(' ')[1] if ' ' in str(latest['timestamp']) else str(latest['timestamp']).split('.')[0]
            col4.metric("⏱️ 最後更新", update_time)
            
            st.divider()
            
            # Charts
            # Convert timestamp to datetime and extract HH:MM:SS
            df['time'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M:%S')
            chart_df = df.sort_values('timestamp')
            
            # Melt the dataframe for altair
            melted_df = chart_df.melt(id_vars=['time'], value_vars=['temperature', 'humidity'], var_name='Metric', value_name='Value')
            
            # Rename for display
            melted_df['Metric'] = melted_df['Metric'].map({'temperature': '溫度 (°C)', 'humidity': '濕度 (%)'})
            
            st.subheader("📈 溫濕度平滑趨勢圖")
            
            # Interactive hover selection
            hover = alt.selection_point(fields=['time'], nearest=True, on='mouseover', empty=False)

            # 計算資料上下限並給予 20% 的延伸空間，避免折線貼齊邊緣
            min_val = melted_df['Value'].min()
            max_val = melted_df['Value'].max()
            padding = (max_val - min_val) * 0.2 if max_val != min_val else 5
            
            # Base smooth line chart
            base_line = alt.Chart(melted_df).mark_line(
                interpolate='monotone', strokeWidth=3
            ).encode(
                x=alt.X('time:N', title='時間', axis=alt.Axis(labelAngle=-45, labelOverlap=True)),
                y=alt.Y('Value:Q', title='數值', scale=alt.Scale(domain=[min_val - padding, max_val + padding])),
                color=alt.Color('Metric:N', 
                              scale=alt.Scale(domain=['溫度 (°C)', '濕度 (%)'], range=['#f1f0ea', '#4DD0E1']),
                              legend=alt.Legend(title="指標", orient='bottom'))
            )

            # Highlight points on hover
            points = base_line.mark_point(size=80, filled=True).encode(
                opacity=alt.condition(hover, alt.value(1), alt.value(0)),
                tooltip=['time', 'Metric', 'Value']
            )

            # Vertical dashed rule on hover
            rule = alt.Chart(melted_df).mark_rule(color='#e0ddcf', strokeDash=[4, 4]).encode(
                x='time:N',
                opacity=alt.condition(hover, alt.value(0.5), alt.value(0)),
                tooltip=['time', 'Metric', 'Value']
            ).add_params(hover)

            # Combine layers
            smooth_chart = alt.layer(base_line, rule, points).properties(
                height=450
            ).interactive()
            
            st.altair_chart(smooth_chart, width='stretch')
            
            with st.expander("🔍 檢視近期歷史數據表格"):
                st.dataframe(df.head(100), width='stretch')
        else:
            st.warning("⏳ 正在等待 ESP32 感測器資料庫寫入...")
            
    time.sleep(2)
