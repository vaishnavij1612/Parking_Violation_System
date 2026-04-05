from backend.ml_models import *
from backend.alpr import recognize_plate


print("Confidence Gate Test:")
print(confidence_gate(0.9))


print("\nAnomaly Detection Test:")
print(detect_anomaly(10))


print("\nFine Prediction Test:")
print(predict_fine(3,14,2,1))