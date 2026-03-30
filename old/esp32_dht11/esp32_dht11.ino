#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// 替換為你的 Wi-Fi 帳號密碼
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 替換為你的電腦內部 IP 地址，例如 192.168.1.100
// 且 API 跑在 5000 port
const char* serverName = "http://192.168.1.100:5000/api/data";

// 定義 DHT 腳位與類型
#define DHTPIN 4     // 修改為你實際接的 PIN 腳
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // 連線到 Wi-Fi
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
  // 檢查 Wi-Fi 連線狀態
  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    
    // 讀取溫度與濕度
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    
    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Failed to read from DHT sensor!");
      delay(2000);
      return;
    }
    
    // 設定 API URL 並宣告要發送 JSON
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    
    // 建構 JSON payload
    // ESP32 Arduino 也可以用 ArduinoJson 函式庫，但這是一個純字串拼接的簡單作法
    String httpRequestData = "{\"temperature\":\"" + String(temperature) + 
                             "\",\"humidity\":\"" + String(humidity) + 
                             "\",\"data_source\":\"esp32\"}";
                             
    // 發送 HTTP POST 請求
    int httpResponseCode = http.POST(httpRequestData);
    
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    Serial.print("Sent URL: ");
    Serial.println(serverName);
    Serial.print("Payload: ");
    Serial.println(httpRequestData);
    
    // 釋放資源
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
  
  // ESP32 真實感測資料每 2 秒更新一次
  delay(2000); 
}
