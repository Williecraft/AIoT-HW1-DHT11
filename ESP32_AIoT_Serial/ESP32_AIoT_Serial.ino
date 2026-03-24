#include <SimpleDHT.h>

// ========== 【1】硬體腳位設定 ==========
// 依照您之前 DHT11.ino 的設定，資料線連接到 GPIO 13
const int pinDHT11 = 13; 
SimpleDHT11 dht11;
// ==========================================

void setup() {
  // 設定為 9600 Baud rate (符合您原本的設定)
  Serial.begin(9600);
  delay(1000);
  Serial.println("ESP32 Serial Sensor Mode Started");
}

void loop() {
  byte temperature = 0;
  byte humidity = 0;
  int err = SimpleDHTErrSuccess;
  
  // 嘗試讀取 DHT11
  if ((err = dht11.read(pinDHT11, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    // 若讀取失敗，輸出錯誤 JSON
    Serial.print("{\"error\": \"Read DHT11 failed\", \"code\": "); 
    Serial.print(err);
    Serial.println("}");
    delay(2000);
    return;
  }
  
  // 組裝 JSON 字串格式，與 WiFi 版格式一致
  // WiFi SSID 設定為 "OFFLINE_SERIAL"，RSSI 設定為 0 方便您在網頁上區分這是 Serial 傳來的資料
  String json = "{\"device_id\":\"esp32_serial_01\", \"wifi_ssid\":\"OFFLINE_SERIAL\", \"wifi_rssi\":0, \"temperature\":" + String((int)temperature) + ", \"humidity\":" + String((int)humidity) + "}";
  
  // 直接透過 Serial 輸出 JSON，交由 Python 橋接腳本去讀取這行並送給 API
  Serial.println(json);
  
  // 延遲 5 秒後進行下一次測量
  delay(5000);
}
