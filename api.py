from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'aiotdb.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('DROP TABLE IF EXISTS sensors')
        c.execute('''
            CREATE TABLE IF NOT EXISTS sensors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                wifi_ssid TEXT,
                wifi_rssi INTEGER,
                temperature REAL,
                humidity REAL,
                timestamp TEXT
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error during init_db: {e}")
    finally:
        conn.close()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/sensor', methods=['POST'])
def sensor_data():
    from datetime import datetime
    data = request.json
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        timestamp = data.get('timestamp')
        if not timestamp:
            timestamp = datetime.now().isoformat()
            
        c.execute('''
            INSERT INTO sensors (device_id, wifi_ssid, wifi_rssi, temperature, humidity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('device_id'),
            data.get('wifi_ssid'),
            data.get('wifi_rssi'),
            data.get('temperature'),
            data.get('humidity'),
            timestamp
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    # In order to exit cleanly if needed, but normally runs indefinitely
    app.run(host='0.0.0.0', port=5000, debug=False)
