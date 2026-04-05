from datetime import datetime

from backend.ml_models import (
    confidence_gate,
    detect_anomaly,
    predict_fine,
    zone_risk_prediction
)


def evaluate_violation(
        plate,
        confidence,
        dwell_time,
        plate_freq,
        zone
):

    if not confidence_gate(confidence):

        return {
            "status": "low_confidence"
        }

    now = datetime.now()

    hour = now.hour
    day = now.weekday()

    anomaly = detect_anomaly(dwell_time)

    fine = predict_fine(
        plate_freq,
        hour,
        day,
        zone,
        dwell_time
    )

    zone_risk = zone_risk_prediction(hour, zone)

    severity_score = 0

    if anomaly:
        severity_score += 2

    if plate_freq > 1:
        severity_score += 2

    if zone_risk == "HIGH":
        severity_score += 1


    if severity_score <= 1:
        severity = "LOW"

    elif severity_score <= 3:
        severity = "MEDIUM"

    else:
        severity = "HIGH"


    return {

        "status": "violation",

        "plate": plate,

        "fine": fine,

        "anomaly": anomaly,

        "zone_risk": zone_risk,

        "severity": severity
    }