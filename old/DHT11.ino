#include <SimpleDHT.h>

// 宣告 DHT11 資料線連接到 ESP32 的腳位 (這裡使用 GPIO 15)
int pinDHT11 = 13; 
SimpleDHT11 dht11; 

void setup() {
  // 初始化 Serial Port，Baud rate (通訊速率) 設為 9600
  Serial.begin(9600);
}

void loop() {
  byte temperature = 0;
  byte humidity = 0;
  int err = SimpleDHTErrSuccess; // 用來儲存感測器讀取狀態的變數

  Serial.println("=================================");
  
  // 嘗試讀取 DHT11 資料
  // dht11.read() 若成功抓到數據，會回傳 SimpleDHTErrSuccess
  if ((err = dht11.read(pinDHT11, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    Serial.print("Read DHT11 failed, err=");
    Serial.println(err);
    // 發生錯誤時，等待 1 秒後再重新嘗試
    delay(1000);
    return;
  }

  // 成功讀取後，將濕度與溫度輸出到 Serial Monitor
  Serial.print("Humidity = "); 
  Serial.print((int)humidity);
  Serial.print("% , ");
  
  Serial.print("Temperature = "); 
  Serial.print((int)temperature);
  Serial.println("C ");
  
  // 【重要】DHT11 的取樣頻率最高只有 0.5Hz，也就是「規定最快每 2 秒只能讀取一次」。
  // 為了穩定性，這裡設定延遲 3000 毫秒 (3 秒) 後再進行下一次測量。
  delay(3000); 
}
