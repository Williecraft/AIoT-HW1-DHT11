# 開發對話日誌 (AI Collaboration Development Log)

> 本檔記錄 AIoT-HW1-DHT11 專案開發期間，與 AI 助理（Claude / Claude Code）協作的完整對話歷程，
> 涵蓋從零建立全棧系統、雙軌（真實 + 模擬）資料源整合、儀表板美化、離線硬體相容，到 Streamlit Cloud 雲端部署的迭代過程。
> 格式為「🧑 我（開發者）」與「🤖 AI」交替，並附上每階段的關鍵產出與決策理由。

---

## 階段一：建立全棧骨架 (Bootstrap)

**🧑 我：**
> 幫我在這個 workspace 建一個本機 Python AIoT demo：`esp32_sim.py` 每隔幾秒用 HTTP POST 把假的 DHT11 溫濕度（含 WiFi 中繼資料）送到 Flask 的 `/sensor`；Flask 寫進 SQLite 的 `aiotdb.db`（`sensors` 表）；Streamlit 讀 SQLite 顯示 KPI、表格、溫度圖、濕度圖。把所有檔案建好、裝好依賴、跑起來、驗證 `/health`、驗證 DB 有寫入、驗證 Streamlit 能啟動。不要加 WiFi 延遲或封包遺失模擬。

**🤖 AI：**
已建立四個核心檔案並完成驗證：
- `api.py`：Flask，含 `/health`（liveness 探針）與 `/sensor`（解析 JSON 後參數化寫入 SQLite）。
- `esp32_sim.py`：每 2 秒以 `random` 產生 20~30°C、40~60% 與浮動 RSSI，POST 到 `/sensor`。
- `app.py`：Streamlit 讀取最新 100 筆，顯示 KPI 與雙圖。
- `requirements.txt`：flask / streamlit / pandas / requests。

驗證結果：`/health` 回 200、SQLite 成功 INSERT、Streamlit 於 `http://localhost:8501` 正常啟動。

**🧑 我：** 先解釋目前每個檔案都在幹嘛。

**🤖 AI：**（逐一說明資料流：模擬器 → Flask → SQLite → Streamlit 的單向管線，並指出 `/sensor` 為唯一寫入點、`app.py` 每 2 秒輪詢資料庫。）

---

## 階段二：清理舊架構與環境調整 (Cleanup)

**🧑 我：** 之前還有用 PHP / MySQL 做過的 `addData.py`、`addData.php` 那些呢？幫我保留最新的 SQLite 版本，其他全部丟到一個資料夾。

**🤖 AI：**
已將舊版 MySQL + HTTP GET 體系（`DHT11.ino`、`addData.php`、`addData.py`、`schema.sql`、`index.html` 等）封存至 `old/` 目錄備查，主目錄僅保留現行 SQLite + Flask POST 架構。理由：舊版環境建置成本高（需 Apache/XAMPP + MySQL）、且 GET 帶參數不符 RESTful 規範。

**🧑 我：** 不要用虛擬環境。

**🤖 AI：** 已移除 venv 相依，改用 Global Python，達成 `pip install -r requirements.txt` 後即可隨插即用。

---

## 階段三：接上真實硬體（真實資料源）

**🧑 我：** 我要接真的 ESP32 + DHT11。先給我 WiFi 版的 `.ino`。

**🤖 AI：**
提供 `ESP32_AIoT_Wifi.ino`：以 `SimpleDHT` 讀 GPIO 13 的 DHT11，`<WiFi.h>` 連線後用 `HTTPClient` POST JSON（含真實 `wifi_rssi`）到 `http://<你的電腦IP>:5000/sensor`，每 2 秒一次。Serial Monitor 看到 `HTTP Response code: 201` 即代表成功寫入後端。

**🧑 我：** 我現場有時候沒 WiFi，能不能用 USB 線直接傳？

**🤖 AI：**
新增「有線降級模式」：
- `ESP32_AIoT_Serial.ino`：不需設定帳密與 IP，直接 `Serial.println()` 吐出與 WiFi 版相同結構的 JSON（`wifi_ssid="OFFLINE_SERIAL"`、`wifi_rssi=0`）。
- `serial_to_api.py`：電腦端監聽 COM 埠，把每行 JSON 轉發給 Flask。

**🧑 我：** 我一跑 Python 程式 ESP32 就一直重開機，怎麼辦？

**🤖 AI：**
這是 `pyserial` 連線瞬間拉動 ESP32 的 DTR/RTS，誤觸 EN/BOOT 重置腳位導致的。已在開啟連線後加入：
```python
ser.setDTR(False)
ser.setRTS(False)
```
加上這兩行即可解除自動重啟鎖死。另外也加了純文字相容：若燒的是舊版 `DHT11.ino`（輸出 `Humidity = 30% , Temperature = 23C`），用正則表達式 `re.search()` 也能擷取數值，不限定 JSON 格式。

---

## 階段四：儀表板美化與互動 (UI/UX)

**🧑 我：** 圖表上的時間只要時分秒就好，不用日期。另外溫濕度兩張圖合併成一張，用不同顏色的線。

**🤖 AI：** 已將時間格式化為 `HH:MM:SS`，並用 `melt` 把溫度、濕度疊進同一張 Altair 圖，以 `color` 區分兩條線。

**🧑 我：** 幫我把網頁弄炫一點，圖表的線用連續平滑的，不要直直的折線。

**🤖 AI：**
- 注入 `@keyframes gradientBG` CSS，背景做成緩慢流動的漸層。
- 折線改 `mark_line(interpolate='monotone', strokeWidth=3)`，曲線平滑如水波。

**🧑 我：** 線上的白點很醜，而且圖例擋到圖了。

**🤖 AI：** 已移除常駐圓點（改為僅 hover 時顯示），並將圖例 `orient='bottom'` 移到圖表下方，橫向空間最大化。

**🧑 我：** 背景幫我改成這組色 `["474448","2d232e","e0ddcf","534b52","f1f0ea"]`。

**🤖 AI：** 已套用此五色莫蘭迪調色盤至漸層背景、KPI 數值色，並寫進 `.streamlit/config.toml` 統一主題。

**🧑 我：** 溫度跟濕度兩條線現在都白色看不出來，濕度幫我改成好看的淺藍。

**🤖 AI：** 已將濕度線改為 `#4DD0E1` 淺藍、溫度維持 `#f1f0ea` 米白，雙線對比清晰。

**🧑 我：** 幫我加一個滑鼠移上去會顯示一條豎虛線，標出那個時間點的溫濕度。

**🤖 AI：** 已用 `alt.selection_point(nearest=True, on='mouseover')` 搭配 `mark_rule(strokeDash=[4,4])` 垂直虛線與 tooltip，實作 hover 追蹤。

---

## 階段五：自動化與防呆 (Automation)

**🧑 我：** 每次都要開三個視窗很煩，幫我寫一個 bat 一鍵啟動。

**🤖 AI：**
已建立 `start_all.bat`，用 `start "" cmd.exe /k` 並行拉起 API、Streamlit、Serial 橋接器三個視窗；並強制 `PYTHONIOENCODING=utf-8`、`PYTHONUNBUFFERED=1`，解決 Windows CMD 輸出中文 / Emoji 崩潰與日誌卡快取的問題。

**🧑 我：** 啟動時先清空，從白圖表開始；圖表範圍要比最大最小值再多一點，不要貼邊。

**🤖 AI：**
- `api.py` 的 `init_db()` 加 `DROP TABLE IF EXISTS sensors`，每次重啟都從乾淨圖表開始。
- `app.py` 加 `padding = (max_val - min_val) * 0.2`，Y 軸上下各留白 20%，折線不再貼齊邊緣。

---

## 階段六：作業要求對齊與雲端部署 (Deployment)

**🧑 我：** 作業要求要有「真實 + 模擬」兩部分、GitHub、Vercel 或 Streamlit 的 live demo、還有 development log。我真實的有做，但圖表的資料源在雲端跑不起來。

**🤖 AI：**
診斷：原 `app.py` 依賴本機 `api.py` 持續寫入 SQLite，且每次啟動 `DROP TABLE`，所以丟到 Streamlit Cloud 會永遠停在「等待資料」。
解法：將 `app.py` 改為**雙模式資料源自動切換**——
1. 本機偵測到 SQLite 有即時資料 → 走 `LIVE` 即時連線模式。
2. 雲端偵測不到 → 回放封存的真實量測快照 `data/real_data.csv`，以 `st.session_state` 滑動視窗逐筆推進，曲線持續流動。

同時匯出 `data/real_data.csv`（實機量測快照，`device_id=esp32_real_01`），讓線上 Demo 重現實機效果。

**🧑 我：** 那 development log 也幫我補齊。

**🤖 AI：**
提供兩份日誌：
- `log.md`：架構演進與優化摘要。
- `chat.md`（本檔）：完整協作對話紀錄。

**🤖 AI（總結）：**
最終交付滿足 HW1 全部要求：
- ✅ 真實資料源：ESP32 + DHT11（WiFi / 有線兩途徑），量測封存於 `aiotdb.db` 與 `data/real_data.csv`。
- ✅ 模擬資料源：`esp32_sim.py`。
- ✅ GitHub：開源倉庫含完整提交歷史。
- ✅ Live Demo：Streamlit Cloud 公開網址，回放真實量測快照。
- ✅ Development Log：`log.md` + `chat.md`。

---

*（本對話日誌為專案開發歷程之整理彙編，部分用語經編修以利閱讀。）*
