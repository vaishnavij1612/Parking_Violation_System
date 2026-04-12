from datetime import datetime
import re
from backend.ml_models import confidence_gate, detect_anomaly, predict_fine, zone_risk_prediction


def is_valid_plate(text):
    if not text:
        return False
    text = text.replace(" ", "").replace("-", "").upper()
    return re.match(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{3,4}$', text)


def evaluate_violation(plate, confidence, dwell_time, plate_freq, zone):

    print("OCR:", plate)

    if not is_valid_plate(plate):
        return {"status": "invalid_plate"}

    if not confidence_gate(confidence):
        return {"status": "low_confidence"}

    now = datetime.now()
    anomaly = detect_anomaly(dwell_time)

    fine = predict_fine(plate_freq, now.hour, now.weekday(), zone, dwell_time)
    zone_risk = zone_risk_prediction(now.hour, zone)

    severity = "LOW"
    if anomaly or plate_freq > 1:
        severity = "MEDIUM"
    if anomaly and zone_risk == "HIGH":
        severity = "HIGH"

    return {
        "status": "violation",
        "plate": plate,
        "fine": fine,
        "anomaly": anomaly,
        "zone_risk": zone_risk,
        "severity": severity
    }