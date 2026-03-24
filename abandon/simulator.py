import requests
import time
import random

# Flask API 網址
API_URL = "http://localhost:5000/api/data"

def generate_and_send_data():
    while True:
        # 假造溫度區間 20 ~ 35，濕度區間 40 ~ 70
        temperature = round(random.uniform(20.0, 35.0), 2)
        humidity = round(random.uniform(40.0, 70.0), 2)
        
        payload = {
            "temperature": temperature,
            "humidity": humidity,
            "data_source": "simulator"
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 201:
                print(f"[Simulator] Sent: Temp={temperature}C, Humid={humidity}%")
            else:
                print(f"[Simulator] Failed to send: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[Simulator] API Connection Error: {e}")
            
        # 模擬資料每 1 秒產生一次
        time.sleep(1)

if __name__ == "__main__":
    print("Starting simulated data generator...")
    generate_and_send_data()
