from datetime import datetime

from ml_models import (
    confidence_gate,
    detect_anomaly,
    predict_fine
)


def evaluate_violation(plate,confidence,dwell_time,plate_freq,zone):

    if not confidence_gate(confidence):

        return {
            "status":"low_confidence"
        }

    hour = datetime.now().hour
    day = datetime.now().weekday()

    anomaly = detect_anomaly(dwell_time)

    fine = predict_fine(
        plate_freq,
        hour,
        day,
        zone
    )

    severity_score = 0

    if anomaly:
        severity_score += 2

    if plate_freq > 1:
        severity_score += 3

    if hour > 17:
        severity_score += 1


    if severity_score >= 5:
        level = "HIGH"
    elif severity_score >= 3:
        level = "MEDIUM"
    else:
        level = "LOW"


    return {

        "status":"violation",

        "plate":plate,

        "fine":fine,

        "anomaly":anomaly,

        "severity":level
    }