from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# 讀取資料庫連線設定
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='aiotdb',
            user='test123',
            password='test123'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# 新增資料 API
@app.route('/aiot/<temp>/<humid>', methods=['GET'])
def add_data(temp, humid):
    try:
        # 將字串轉換為浮點數
        temp_val = float(temp)
        humid_val = float(humid)
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # 準備 SQL 查詢，使用參數化查詢防止 SQL Injection
        sql = "INSERT INTO sensor (temp, humid) VALUES (%s, %s)"
        val = (temp_val, humid_val)
        
        cursor.execute(sql, val)
        conn.commit()
        
        return jsonify({
            "status": "success", 
            "message": f"Data inserted successfully. Temp: {temp_val}, Humid: {humid_val}"
        }), 200
        
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid parameters. Temp and humid must be numbers."}), 400
    except Error as e:
        return jsonify({"status": "error", "message": f"Database error: {e}"}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    # 預設跑在 port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
