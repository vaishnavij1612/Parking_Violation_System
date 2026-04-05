import os
import sys
import time
from datetime import datetime

# Add project root to sys.path so 'backend' is importable as a package
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request, render_template
from alpr import recognize_plate
from ml_pipeline import evaluate_violation
from database import get_db_connection, insert_violation


# Flask app with template/static folders relative to project root
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR   = os.path.join(PROJECT_ROOT, 'static')

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "success",
        "message": "Server Running"
    }), 200


@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Read and validate dwell time
        dwell_time_str = request.headers.get('Dwell-Time')
        if not dwell_time_str:
            return jsonify({
                "status": "error",
                "message": "Missing 'Dwell-Time' header"
            }), 400
            
        try:
            dwell_time = int(dwell_time_str)
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid 'Dwell-Time', must be an integer"
            }), 400
            
        print(f"[INFO] Dwell Time recorded: {dwell_time} seconds")

        image_bytes = request.data
        if not image_bytes:
            return jsonify({
                "status": "error",
                "message": "No image data provided"
            }), 400

        # Generate filename
        timestamp = int(time.time() * 1000)
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        # Relative path (important for frontend later)
        relative_path = f"images/{filename}"

        print(f"[INFO] Image saved at: {filepath}")

        # ALPR Integration
        plate, confidence = recognize_plate(filepath)

        # Handle No Plate Detected
        if plate is None:
            print(f"[WARNING] No plate detected for image: {filepath}")
            return jsonify({
                "status": "error",
                "message": "No license plate detected"
            }), 400

        print(f"[INFO] Plate detected: {plate} | Confidence: {confidence}")

        # ML Pipeline: confidence gate + anomaly detection + fine prediction
        # Placeholder values for plate_freq and zone until real data is available
        result = evaluate_violation(
            plate=plate,
            confidence=confidence,
            dwell_time=dwell_time,
            plate_freq=1,
            zone=1
        )

        if result["status"] == "low_confidence":
            print(f"[WARNING] Confidence gate failed for plate: {plate} (Confidence: {confidence})")
            return jsonify({
                "status": "error",
                "message": "Confidence gate failed — plate reading not reliable",
                "plate": plate,
                "confidence": confidence
            }), 400

        is_anomaly = result["anomaly"]
        fine_amount = result["fine"]
        severity    = result["severity"]

        print(f"[INFO] Anomaly: {is_anomaly} | Fine: {fine_amount} | Severity: {severity}")

        # Insert Violation Record into Database
        conn = get_db_connection()
        try:
            insert_violation(conn, plate, timestamp, dwell_time, fine_amount, severity, relative_path)
            conn.commit()
        finally:
            conn.close()

        return jsonify({
            "status": "success",
            "plate": plate,
            "confidence": confidence,
            "dwell_time": dwell_time,
            "fine": fine_amount,
            "anomaly": is_anomaly,
            "severity": severity
        }), 200

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Dashboard page showing only the LATEST violation for each unique plate."""
    conn = get_db_connection()
    try:
        # Query: Find the record with the maximum ID for each unique plate
        # This keeps the "Keep it once" requirement satisfied for the same car.
        rows = conn.execute('''
            SELECT plate, timestamp, dwell_time, fine, severity, image_path 
            FROM violations 
            WHERE id IN (SELECT MAX(id) FROM violations GROUP BY plate) 
            ORDER BY timestamp DESC
        ''').fetchall()

        # Convert rows to dicts and format the timestamp
        violations = []
        for row in rows:
            violations.append({
                "plate":      row["plate"],
                "time":       datetime.fromtimestamp(row["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                "dwell_time": row["dwell_time"],
                "fine":       row["fine"],
                "severity":   row["severity"],
                "image_path": row["image_path"]
            })
    finally:
        conn.close()

    return render_template('index.html', violations=violations)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)