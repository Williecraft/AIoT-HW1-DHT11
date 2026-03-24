# 專案開發與演進日誌 (Project Log)

## 1. 開發歷程與使用者提示詞 (Prompts)
本專案經歷了數次結構調整與優化，以下為開發期間收到的核心指令紀錄：

1. **初始架構建立**：「Create and fully run a local Python AIoT demo in this workspace: esp32_sim.py sends fake DHT11 data with WiFi-connected ESP32 metadata every 5 seconds via HTTP POST to Flask /sensor; Flask stores into SQLite3 aiotdb.db, sensors table; Streamlit reads SQLite and shows KPI, table, temperature chart, humidity chart. Create all files, venv, requirements, install dependencies, run everything, verify /health, verify DB inserts, verify Streamlit startup, auto-fix errors, and report final URLs and rerun commands. Do not add WiFi delay, packet loss, or network simulation.」
2. **詢問各檔案功用**：「先解釋目前每個檔案都在幹嘛」
3. **詢問遺留檔案**：「那 addData.py 呢」與「@[c:\Users\user\Desktop\esp32_dht11\addData.py] 我說的是這個」
4. **清理舊檔案與廢棄架構**：「那幫我保留最新版SQLite版本 其他全部丟到一個資料夾叫做 abandon」
5. **環境設定調整**：「不要用虛擬環境」
6. **儀表板圖表初步優化**：「圖表上顯示的時間只要 小時分秒就好 不用日期。另外我想要溫溼度的圖合併成一個 用不同顏色的線」
7. **產生本篇日誌**：「把整個專案內容、製作prompt、包含abandon裡面以前做的md 甚麼細節都寫進 log.md」
8. **儀表板進階美化 (連貫平滑折線與 UI 升級)**：「幫我美化網頁顯示，讓他炫一點。另外圖表的部分幫我用連續平滑化的線，不要直接的折線圖。所有變更都一併更新到log.md」
9. **圖表細部調整**：「圖上顯示白點很醜 然後圖例擋到了」
10. **全站色系與動態背景客製化**：「幫我網頁的背景風格改成由以下顏色組成 ["474448","2d232e","e0ddcf","534b52","f1f0ea"]。所有變更都一併更新到log.md」
11. **圖表對比度優化**：「溫度和濕度現在線段的顏色一樣了都是白色 幫我一個改好看的淺藍色」
12. **圖表互動功能開發**：「幫我加一個 滑鼠移動上去會顯示一條豎虛線 顯示該時間點的溫溼度」
13. **系統自動化與除錯特化**：「幫我寫一個bat檔 依次執行」、「啟動時先清空 從白圖表開始」、「顯示圖表顯示的範圍要比最大最小值再多一點」：打造防呆一鍵啟動腳本 `start_all.bat`、資料庫熱重啟自清空 (`init_db` DROP)、Serial COM 亂碼修正、舊型純文字測資相容解析與 Y 軸智慧比例延展防貼邊。

---

## 2. 舊版與廢棄架構 (Legacy Architecture - `abandon/`)
在重構為當前的全 Python / SQLite 架構前，專案依賴於 MySQL，並透過 `GET` 請求傳輸資料。舊有的文件與程式碼已全數封存至 `abandon/` 目錄中。

### `abandon/project_report.md` 歷史紀錄細節：
> **專案簡介**
> 本平台實作了兩種不同語言（PHP 與 Python）的資料寫入介面 API，讓硬體端能根據網路與運行環境的受限狀況彈性選擇。
>
> **1. `aiotdb` 資料庫**
> 持久化儲存溫濕度紀錄。包含 `sensor` 資料表：`id`, `temp`, `humid`, `time` (current_timestamp)。
>
> **2. `addData.php` (PHP 實作)**
>  部署在 Apache 伺服器，解析 `GET http://localhost/addData.php?temp={溫度}&humid={濕度}` 來獲取數值。並由 `floatval()` 強制轉換為浮點數型態防範 SQL Injection。
>
> **3. `addData.py` (Python / Flask 實作)**
>  Flask 建立的 REST-like 介面，路由為 `GET http://localhost:5000/aiot/{溫度}/{濕度}`。使用參數化查詢 (`%s`) 防範 SQL Injection。
>
> 總結：PHP 展現隨插即用的輕巧性，而 Python Flask 示範了 JSON 結構化回應及預防資安風險的最佳實踐。

---

## 3. 當前專案架構源碼與細節 (Current Project Architecture)

目前的最新版架構採用：**Flask Backend + SQLite DB + Streamlit Frontend + HTTP POST JSON**。

### 3.1 核心依賴：`requirements.txt`
為了相容最新的 Python 開發環境，取消強綁定版本：
```text
flask
streamlit
pandas
requests
```

### 3.2 後端 API 伺服器：`api.py`
初始化 SQLite 資料庫 `aiotdb.db` 的 `sensors` 表格。並設計兩個獨立端點：`/health` 健康狀態檢查、`/sensor` 接收資料寫入：
*(原始邏輯可參考專案目錄)*

### 3.3 ESP32 軟體模擬器與硬體程式 (`esp32_sim.py`, `ESP32_AIoT.ino`)
* `esp32_sim.py`：純軟體測試用，每隔 2 秒產生隨機溫濕度亂數 (Python 產生器)，送入資料庫。
* `ESP32_AIoT.ino`：整合 WiFi 連線與 `SimpleDHT` 庫的實際硬體 C++ 燒錄檔，直接將硬體感測值 POST 給上述 `api.py`。
*(原始邏輯可參考專案目錄)*

### 3.4 視覺化儀表板佈景主題：`.streamlit/config.toml`
使用了使用者提供的五色調色盤 (`#474448`, `#2d232e`, `#e0ddcf`, `#534b52`, `#f1f0ea`) 構成核心組件配色：
```toml
[theme]
primaryColor="#e0ddcf"
backgroundColor="#2d232e"
secondaryBackgroundColor="#474448"
textColor="#f1f0ea"
```

### 3.5 視覺化儀表板主程式：`app.py`
使用 Streamlit 與 Altair。整合了自訂 CSS 動態漸層背景、互動平滑曲線、無圓點、圖例置底的圖表配置，以及折疊式的表格功能：
```python
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

            # Base smooth line chart
            base_line = alt.Chart(melted_df).mark_line(
                interpolate='monotone', strokeWidth=3
            ).encode(
                x=alt.X('time:N', title='時間', axis=alt.Axis(labelAngle=-45, labelOverlap=True)),
                y=alt.Y('Value:Q', title='數值', scale=alt.Scale(zero=False)),
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
            
            st.altair_chart(smooth_chart, use_container_width=True)
            
            with st.expander("🔍 檢視近期歷史數據表格"):
                st.dataframe(df.head(100), use_container_width=True)
        else:
            st.warning("⏳ 正在等待 ESP32 感測器資料庫寫入...")
            
    time.sleep(2)
```

---

## 4. 近期系統優化與自動化 (Recent Optimizations)

近期針對離線硬體連接不順與使用者體驗進行了大量除錯與強化：

### 4.1 一鍵自動化啟動腳本 (`start_all.bat`)
為解決使用者需手動開啟多個終端機的問題，新增了 `start_all.bat`：
* 利用 `start "" cmd.exe /k` 達成多視窗並行啟動 (API, Streamlit, 橋接器)。
* 強制寫入 `set PYTHONIOENCODING=utf-8` 與 `set PYTHONUNBUFFERED=1`，解決 Windows CMD 預設 CP950 編碼遇到 Emoji 或是中文造成的致命閃退，並確保即時印出收發日誌不動輒被快取卡死。

### 4.2 舊版設備相容與防鎖死 (Serial Bridge 升級)
深度修改了 `serial_to_api.py` 核心：
* **純文字格式解析**：即便硬體端燒錄的是舊版網路上的 DHT11.ino (輸出 `Humidity = 30% , Temperature = 23C` 等純文字)，而非本專案的 JSON 格式，現在能透過 `re` 正則表達式自動辨識並封裝成相容的 JSON 發送。
* **解除 ESP32 連接鎖死**：加入 `ser.setDTR(False)` 與 `ser.setRTS(False)`，防止 `pyserial` 連線瞬間錯誤觸發 ESP32 硬體的 EN/BOOT (Reset) 腳位導致程式無法執行。

### 4.3 視覺延展與資料重置體驗 (Dashboard 優化)
* **自動清空重建**：`api.py` 的 `init_db()` 加入 `DROP TABLE IF EXISTS sensors`，保證每次執行腳本重新啟動系統時，儀表板皆從完全空白的狀態開始繪製，達成「從無到有慢慢浮現」的效果。
* **圖表 Y 軸智慧緩衝**：`app.py` 中加入了動態範圍計算 `padding = (max_val - min_val) * 0.2 if max_val != min_val else 5`，並將算出的 Domain 配置進 Y 軸，讓溫濕度平滑折線不再緊貼視窗上下邊緣。
* **技術債清理**：替換掉即將被棄用的 Streamlit 參數 `use_container_width=True`，全面改用官方推薦的 `width='stretch'` 避免洗版警告。
