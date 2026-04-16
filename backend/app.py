import os
import sys
import time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request, render_template
from alpr import recognize_plate
from ml_pipeline import evaluate_violation
from database import get_db_connection, insert_violation
from notifier import send_telegram_notification

TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR   = os.path.join(PROJECT_ROOT, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 🔥 NEW FUNCTION
def get_last_detection_time(conn, plate):
    row = conn.execute(
        "SELECT timestamp FROM violations WHERE plate = ? ORDER BY id DESC LIMIT 1",
        (plate,)
    ).fetchone()

    if row:
        return row["timestamp"]
    return None


@app.route('/')
def index():
    return jsonify({"status": "success", "message": "Server Running"}), 200


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        dwell_time = int(request.headers.get('Dwell-Time', 0))

        image_bytes = request.data
        if not image_bytes:
            return jsonify({"status": "error"}), 400

        timestamp = int(time.time() * 1000)
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        relative_path = f"images/{filename}"

        # -------- ALPR --------
        plate, confidence = recognize_plate(filepath)

        if plate is None:
            return jsonify({
                "status": "error",
                "plate_detected": False,
                "trigger_buzzer": False
            }), 400

        # -------- ML --------
        result = evaluate_violation(
            plate=plate,
            confidence=confidence,
            dwell_time=dwell_time,
            plate_freq=1,
            zone=1
        )

        if result["status"] == "low_confidence":
            return jsonify({
                "status": "error",
                "plate_detected": False,
                "trigger_buzzer": False
            }), 400

        fine_amount = result["fine"]
        severity = result["severity"]
        is_anomaly = result["anomaly"]

        # 🔥 IMMEDIATE BUZZER (MAIN CHANGE)
        trigger_buzzer = True

        # -------- DB INSERT --------
        conn = get_db_connection()

        insert_violation(
            conn,
            plate,
            timestamp,
            dwell_time,
            fine_amount,
            severity,
            relative_path
        )

        conn.commit()
        conn.close()

        # -------- TELEGRAM --------
        if fine_amount > 0:
            send_telegram_notification(plate, fine_amount, severity)

        return jsonify({
            "status": "success",
            "plate_detected": True,
            "trigger_buzzer": trigger_buzzer,
            "plate": plate,
            "confidence": confidence,
            "dwell_time": dwell_time,
            "fine": fine_amount,
            "anomaly": is_anomaly,
            "severity": severity
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()

    rows = conn.execute('''
        SELECT plate, timestamp, dwell_time, fine, severity, image_path 
        FROM violations 
        WHERE id IN (SELECT MAX(id) FROM violations GROUP BY plate) 
        ORDER BY timestamp DESC
    ''').fetchall()

    violations = []
    for row in rows:
        violations.append({
            "plate": row["plate"],
            "time": datetime.fromtimestamp(row["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
            "dwell_time": row["dwell_time"],
            "fine": row["fine"],
            "severity": row["severity"],
            "image_path": row["image_path"]
        })

    conn.close()
    return render_template('index.html', violations=violations)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)