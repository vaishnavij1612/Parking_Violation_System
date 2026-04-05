from backend.ml_models import (
    confidence_gate,
    detect_anomaly,
    predict_fine,
    zone_risk_prediction
)

# simulate values

confidence = 0.91
dwell_time = 10
plate_freq = 3
hour = 19
day = 2
zone = 2

print("Confidence Gate:", confidence_gate(confidence))

print("Anomaly Detection:", detect_anomaly(dwell_time))

fine = predict_fine(
    plate_freq,
    hour,
    day,
    zone,
    dwell_time
)

print("Predicted Fine:", fine)

print("Zone Risk:", zone_risk_prediction(hour, zone))