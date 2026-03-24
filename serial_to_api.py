import serial
import requests
import json
import time
import sys

# 設定 Serial Port 及 Baud Rate，這邊依照您剛剛舊版腳本的紀錄預設為 COM4
# ⚠️ 如果您的電腦上是 COM3 或是其他名稱，請直接更改這裡！
PORT = 'COM4' 
BAUD_RATE = 9600

# 設定 Flask API 網址 (與我們現在網頁共用的同一組後端)
API_URL = "http://localhost:5000/sensor"

def main():
    print(f"嘗試連接到 Serial Port {PORT} (Baud rate: {BAUD_RATE})...")
    try:
        # 連接實體的 COM Port (加上 timeout 避免死鎖)
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        
        # 針對 ESP32，有時 Python 建立連線會意外把重置腳位 (EN/BOOT) 拉住了，加上這兩行放開控制：
        ser.setDTR(False)
        ser.setRTS(False)
        
        print("✅ 連接成功！正在監聽 ESP32 傳送過來的資料...")
    except serial.SerialException as e:
        print(f"❌ 無法開啟 Serial Port {PORT}: {e}")
        print("💡 請確認您的 ESP32 是不是插在另一個 USB 孔 (例如 COM3 或 COM5)？")
        print("💡 另外，請確保 [Arduino IDE 的 Serial Monitor 已完全關閉]，否則 Port 會被占用！")
        sys.exit(1)

    try:
        while True:
            # 直接讀取 (timeout 為 1 秒，若沒資料會回傳空字串，不會卡死)
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"\n[COM] 收到: {line}")
                
                import re
                
                payload = None
                
                # 情境 1：如果 ESP32 傳進來的是標準 JSON (ESP32_AIoT_Serial.ino 格式)
                if line.startswith("{") and line.endswith("}"):
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        print("   ⚠️ 該行 JSON 格式損毀，略過轉發。")
                
                # 情境 2：如果 ESP32 傳進來的是純文字 (舊版 DHT11.ino 格式)
                else:
                    # 使用正則表達式萃取數字：例如 "Humidity = 30% , Temperature = 23C"
                    temp_match = re.search(r'Temperature\s*=\s*(\d+(?:\.\d+)?)', line, re.IGNORECASE)
                    hum_match = re.search(r'Humidity\s*=\s*(\d+(?:\.\d+)?)', line, re.IGNORECASE)
                    
                    if temp_match and hum_match:
                        payload = {
                            "device_id": "esp32_serial_legacy",
                            "wifi_ssid": "OFFLINE_SERIAL",
                            "wifi_rssi": 0,
                            "temperature": float(temp_match.group(1)),
                            "humidity": float(hum_match.group(1))
                        }
                    elif "===========" not in line and "Started" not in line:
                        print("   ⚠️ 未知資料格式，無法擷取溫濕度。")
                        
                # 確保成功取得 payload 以及內部有溫度資料，再發送給 flask API
                if payload and "temperature" in payload:
                    try:
                        response = requests.post(API_URL, json=payload)
                        print(f"   👉 成功轉發原始溫濕度 {payload['temperature']}°C, {payload['humidity']}% 至戰情室 (狀態碼: {response.status_code})")
                    except requests.exceptions.RequestException as e:
                        print(f"   ❌ 轉發至 API 失敗: {e}")
            
            # 使用微小延遲降低 CPU 負載
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n使用者主動中斷程式 (Ctrl+C)")
    finally:
        ser.close()
        print("Serial 連線已安全關閉。")

if __name__ == '__main__':
    main()
