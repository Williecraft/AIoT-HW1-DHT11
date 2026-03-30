<?php
// 資料庫連線設定
$servername = "localhost";
$username = "test123";
$password = "test123"; // 預設 XAMPP 的 root 沒有密碼
$dbname = "aiotdb";

// 建立連線
$conn = new mysqli($servername, $username, $password, $dbname);

// 檢查連線
if ($conn->connect_error) {
    die("連線失敗: " . $conn->connect_error);
}

// 檢查是否有透過 GET 方法傳遞 temp 和 humid 參數
if (isset($_GET['temp']) && isset($_GET['humid'])) {

    // 取得參數並轉換為浮點數，以防 SQL 隱碼攻擊
    $temp = floatval($_GET['temp']);
    $humid = floatval($_GET['humid']);

    // 準備 SQL 寫入語法
    $sql = "INSERT INTO sensor (temp, humid) VALUES ($temp, $humid)";

    // 執行 SQL 語法並檢查是否成功
    if ($conn->query($sql) === TRUE) {
        echo "新資料寫入成功！溫度: $temp, 濕度: $humid";
    }
    else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
}
else {
    echo "請提供 temp 及 humid 參數，例如：?temp=25.5&humid=60.0";
}

// 關閉連線
$conn->close();
?>
