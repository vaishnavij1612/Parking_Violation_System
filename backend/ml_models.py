import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import IsolationForest


# -------------------------------
# Generate synthetic dataset
# -------------------------------

def generate_dataset():

    rows = []

    for i in range(300):

        plate_freq = np.random.randint(1,5)
        hour = np.random.randint(0,24)
        day = np.random.randint(0,7)
        zone = np.random.randint(1,3)

        if plate_freq == 1:
            fine = 100
        elif plate_freq == 2:
            fine = 300
        else:
            fine = 500

        rows.append([plate_freq,hour,day,zone,fine])

    df = pd.DataFrame(
        rows,
        columns=[
            "plate_freq",
            "hour",
            "day",
            "zone",
            "fine"
        ]
    )

    return df


# -------------------------------
# Train RandomForest
# -------------------------------

def train_repeat_model():

    df = generate_dataset()

    X = df[["plate_freq","hour","day","zone"]]
    y = df["fine"]

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X,y)

    return model


# -------------------------------
# Train IsolationForest
# -------------------------------

def train_anomaly_model():

    dwell_times = [[2],[3],[4],[5],[6],[7]]

    model = IsolationForest(
        contamination=0.15,
        random_state=42
    )

    model.fit(dwell_times)

    return model


# -------------------------------
# Initialize models
# -------------------------------

repeat_model = train_repeat_model()

anomaly_model = train_anomaly_model()


# -------------------------------
# Confidence Gate
# -------------------------------

def confidence_gate(confidence):

    """
    Reject plates with low ALPR confidence
    """

    return confidence >= 0.85


# -------------------------------
# Anomaly Detection
# -------------------------------

def detect_anomaly(dwell_time):

    """
    Detect abnormal parking time
    """

    result = anomaly_model.predict([[dwell_time]])

    if result[0] == -1:
        return True

    return False


# -------------------------------
# Fine Prediction
# -------------------------------

def predict_fine(plate_freq, hour, day, zone):

    """
    Predict fine amount using RandomForest
    """

    features = [[plate_freq, hour, day, zone]]

    fine = repeat_model.predict(features)[0]

    return int(fine)