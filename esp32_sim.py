import time
import random
import requests
import json
from datetime import datetime

API_URL = "http://localhost:5000/sensor"

def generate_sensor_data():
    return {
        "device_id": "esp32_01",
        "wifi_ssid": "IoT_Net_2.4G",
        "wifi_rssi": random.randint(-85, -40),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(40.0, 60.0), 2),
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("Starting ESP32 Simulator...")
    while True:
        data = generate_sensor_data()
        try:
            response = requests.post(API_URL, json=data)
            print(f"Sent: {data} -> Status: {response.status_code}")
        except Exception as e:
            print(f"Error sending data: {e}")
        time.sleep(2)

if __name__ == "__main__":
    main()
