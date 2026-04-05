from backend.ml_pipeline import evaluate_violation

# simulate system inputs

plate = "TN09AB1234"
confidence = 0.92
dwell_time = 9
plate_freq = 2
zone = 2

result = evaluate_violation(
    plate,
    confidence,
    dwell_time,
    plate_freq,
    zone
)

print(result)