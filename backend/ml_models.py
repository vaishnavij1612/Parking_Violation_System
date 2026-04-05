import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import IsolationForest


# -----------------------------
# Zone definitions
# -----------------------------

ZONE_TYPES = {
    1: "Residential",
    2: "Market",
    3: "Transit"
}


# -----------------------------
# Generate semi-realistic dataset
# -----------------------------

def generate_dataset(n_samples=500):

    rows = []

    for _ in range(n_samples):

        plate_freq = np.random.randint(1,5)
        hour = np.random.randint(0,24)
        day = np.random.randint(0,7)
        zone = np.random.choice([1,2,3])

        # realistic dwell patterns

        if zone == 1:
            dwell_time = np.random.randint(2,6)

        elif zone == 2:
            dwell_time = np.random.randint(5,10)

        else:
            dwell_time = np.random.randint(4,8)

        violation_score = 0

        if plate_freq > 1:
            violation_score += 2

        if hour >= 17:
            violation_score += 1

        if zone == 2:
            violation_score += 1

        if dwell_time > 8:
            violation_score += 1

        if violation_score <= 1:
            fine = 100

        elif violation_score <= 3:
            fine = 300

        else:
            fine = 500

        rows.append([
            plate_freq,
            hour,
            day,
            zone,
            dwell_time,
            fine
        ])

    df = pd.DataFrame(
        rows,
        columns=[
            "plate_freq",
            "hour",
            "day",
            "zone",
            "dwell_time",
            "fine"
        ]
    )

    return df


# -----------------------------
# Train RandomForest model
# -----------------------------

def train_fine_model():

    df = generate_dataset()

    X = df[[
        "plate_freq",
        "hour",
        "day",
        "zone",
        "dwell_time"
    ]]

    y = df["fine"]

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model


# -----------------------------
# Train anomaly detector
# -----------------------------

def train_anomaly_model():

    normal_dwell_times = [[2],[3],[4],[5],[6],[7]]

    model = IsolationForest(
        contamination=0.15,
        random_state=42
    )

    model.fit(normal_dwell_times)

    return model


# -----------------------------
# Initialize models
# -----------------------------

fine_model = train_fine_model()
anomaly_model = train_anomaly_model()


# -----------------------------
# ML Functions
# -----------------------------

def confidence_gate(confidence):

    return confidence >= 0.85


def detect_anomaly(dwell_time):

    result = anomaly_model.predict([[dwell_time]])

    return bool(result[0] == -1)


def predict_fine(
        plate_freq,
        hour,
        day,
        zone,
        dwell_time
):

    features = [[
        plate_freq,
        hour,
        day,
        zone,
        dwell_time
    ]]

    fine = fine_model.predict(features)

    return int(fine[0])


def zone_risk_prediction(hour, zone):

    risk_score = 0

    if hour >= 17:
        risk_score += 2

    if zone == 2:
        risk_score += 2

    if zone == 3:
        risk_score += 1

    if risk_score <= 1:
        return "LOW"

    elif risk_score <= 3:
        return "MEDIUM"

    else:
        return "HIGH"