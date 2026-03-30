import serial
import sqlite3
import datetime
import re
import time
import sys

# 設定 Serial Port 及 Baud Rate，請根據你的電腦修改 (例如 Windows 的 COM3，Linux/Mac 的 /dev/ttyUSB0)
PORT = 'COM4' 
BAUD_RATE = 9600

# 設定 SQLite 資料庫檔案名稱
DB_NAME = 'atoidb.db'

def create_table(cursor):
    """建立資料表"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL
        )
    ''')

def main():
    # 連線到 SQLite 資料庫（若檔案不存在會自動建立）
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    create_table(cursor)
    conn.commit()

    print(f"嘗試連接到 Serial Port {PORT} at {BAUD_RATE} baud...")
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        print("連接成功！開始讀取資料...")
    except serial.SerialException as e:
        print(f"無法開啟 Serial Port {PORT}: {e}")
        print("請確認 Port 名稱正確，並且 ESP32 已經連接且未被 Arduino IDE 的 Serial Monitor 佔用。")
        sys.exit(1)

    # 根據 Arduino 程式的輸出格式:
    # "Humidity = 45% , Temperature = 24C "
    pattern = re.compile(r"Humidity\s*=\s*(\d+(?:\.\d+)?)[^T]*Temperature\s*=\s*(\d+(?:\.\d+)?)")

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"收到: {line}")
                    
                    match = pattern.search(line)
                    if match:
                        humidity_str = match.group(1)
                        temperature_str = match.group(2)
                        
                        try:
                            humidity = float(humidity_str)
                            temperature = float(temperature_str)
                            
                            # 取得當前時間
                            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            # 寫入 SQLite
                            cursor.execute('''
                                INSERT INTO sensors (timestamp, temperature, humidity)
                                VALUES (?, ?, ?)
                            ''', (current_time, temperature, humidity))
                            
                            conn.commit()
                            print(f"[{current_time}] 已將資料存入資料庫: 溫度={temperature}C, 濕度={humidity}%")
                            
                        except ValueError:
                            print("數值轉換錯誤")
            # 加上短暫延遲降低 CPU 使用率
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n使用者中斷程式 (Ctrl+C)")
    finally:
        ser.close()
        conn.close()
        print("資源已釋放，資料庫連線已關閉。")

if __name__ == '__main__':
    main()
