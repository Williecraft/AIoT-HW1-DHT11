#include <WiFi.h>
#include <HTTPClient.h>
#include <SimpleDHT.h>

// ========== 【1】網路與 API 設定 ==========
const char* ssid = "YOUR_WIFI_SSID";           // 請替換為您的 WiFi 名稱
const char* password = "YOUR_WIFI_PASSWORD";   // 請替換為您的 WiFi 密碼

// 請將 <YOUR_COMPUTER_IP> 替換成執行 Flask API 電腦的內部 IP (例如: 192.168.0.100)
const char* serverName = "http://<YOUR_COMPUTER_IP>:5000/sensor"; 
// ==========================================

// ========== 【2】硬體腳位設定 ==========
// 依照您之前 DHT11.ino 的設定，資料線連接到 GPIO 13
const int pinDHT11 = 13; 
SimpleDHT11 dht11;
// ==========================================

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  // 開始連接 WiFi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 確認 WiFi 是否還連線中
  if(WiFi.status() == WL_CONNECTED){
    
    byte temperature = 0;
    byte humidity = 0;
    int err = SimpleDHTErrSuccess;
    
    // 嘗試讀取 DHT11
    if ((err = dht11.read(pinDHT11, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
      Serial.print("Read DHT11 failed, err="); 
      Serial.println(err);
      delay(2000); // 失敗的話等 2 秒再試
      return;
    }
    
    // 取得 WiFi 訊號強度 (RSSI)
    int rssi = WiFi.RSSI();
    
    // 建立 HTTP 客戶端
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json"); // 指定傳送 JSON 格式
    
    // 將資料打包成 JSON 字串格式
    // 格式為: {"device_id":"esp32_real_01", "wifi_ssid":"...", "wifi_rssi":-50, "temperature":25, "humidity":60}
    String httpRequestData = "{\"device_id\":\"esp32_real_01\", \"wifi_ssid\":\"" + String(ssid) + "\", \"wifi_rssi\":" + String(rssi) + ", \"temperature\":" + String((int)temperature) + ", \"humidity\":" + String((int)humidity) + "}";
    
    Serial.println("=================================");
    Serial.println("Sending Data to API:");
    Serial.println(httpRequestData);
    
    // 發送 HTTP POST 請求
    int httpResponseCode = http.POST(httpRequestData);
    
    // 檢查回傳狀態碼 (201 代表成功建立)
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    }
    else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode); // 負數代表網路連線失敗
    }
    
    // 釋放資源
    http.end();
  }
  else {
    Serial.println("WiFi Disconnected");
  }
  
  // 配合我們原先模擬器的頻率，每 5 秒上傳一次
  delay(5000);
}
