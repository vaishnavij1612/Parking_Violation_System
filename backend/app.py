import os
import sys
import time
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request, render_template
from alpr import recognize_plate, crop_number_plate
from ml_pipeline import evaluate_violation
from database import get_db_connection, insert_violation

import cv2

TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR   = os.path.join(PROJECT_ROOT, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "success", "message": "Server Running"}), 200


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # -------- Dwell Time --------
        dwell_time = int(request.headers.get('Dwell-Time', 0))

        # -------- Image --------
        image_bytes = request.data
        if not image_bytes:
            return jsonify({"status": "error", "message": "No image"}), 400

        timestamp = int(time.time() * 1000)
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        print(f"[INFO] Image saved: {filepath}")

        # -------- Crop Plate FIRST --------
        cropped = crop_number_plate(filepath)

        if cropped is None:
            return jsonify({
                "status": "error",
                "message": "No plate region found"
            }), 400

        cropped_filename = f"plate_{timestamp}.jpg"
        cropped_path = os.path.join(UPLOAD_FOLDER, cropped_filename)
        cv2.imwrite(cropped_path, cropped)

        relative_path = f"images/{cropped_filename}"

        # -------- OCR --------
        plate, confidence = recognize_plate(cropped_path)

        if plate is None:
            return jsonify({
                "status": "error",
                "message": "No plate detected"
            }), 400

        print(f"[INFO] Plate: {plate} | Confidence: {confidence}")

        # -------- ML --------
        zone = int(request.headers.get('Zone', 1))
        plate_freq = int(request.headers.get('Frequency', 1))

        result = evaluate_violation(
            plate=plate,
            confidence=confidence,
            dwell_time=dwell_time,
            plate_freq=plate_freq,
            zone=zone
        )

        # 🚨 Invalid plate
        if result["status"] == "invalid_plate":
            return jsonify({"status": "error", "message": "Invalid plate"}), 400

        # 🚨 Low confidence
        if result["status"] == "low_confidence":
            return jsonify({"status": "error", "message": "Low confidence"}), 400

        # -------- Save DB --------
        conn = get_db_connection()
        try:
            insert_violation(
                conn,
                plate,
                timestamp,
                dwell_time,
                result["fine"],
                result["severity"],
                relative_path
            )
            conn.commit()
        finally:
            conn.close()

        return jsonify({
            "status": "success",
            "plate": plate,
            "fine": result["fine"],
            "severity": result["severity"]
        }), 200

    except Exception as e:
        print("[ERROR]", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = get_db_connection()
    try:
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
                "time": datetime.fromtimestamp(row["timestamp"]/1000).strftime("%Y-%m-%d %H:%M:%S"),
                "dwell_time": row["dwell_time"],
                "fine": row["fine"],
                "severity": row["severity"],
                "image_path": row["image_path"]
            })
    finally:
        conn.close()

    return render_template('index.html', violations=violations)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)