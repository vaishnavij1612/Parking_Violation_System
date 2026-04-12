import requests
import json
import os

# --- Configuration ---
URL        = "http://127.0.0.1:5000/upload"
IMAGE_FILE = "car.png"
DWELL_TIME = "15"
ZONE       = "2"  # 1=Residential, 2=Market, 3=Transit
FREQUENCY  = "5"  # How many times this car has been seen




def test_upload():

    # 1. Check if the image file exists
    if not os.path.exists(IMAGE_FILE):
        print(f"[ERROR] Image file '{IMAGE_FILE}' not found.")
        print("        Place 'car.jpg' in the project root directory and try again.")
        return

    # 2. Read the image as raw binary
    with open(IMAGE_FILE, "rb") as f:
        image_bytes = f.read()

    print(f"[INFO] Sending '{IMAGE_FILE}' ({len(image_bytes)} bytes) to {URL}")

    # 3. Send POST request with raw binary body and Dwell-Time header
    try:
        response = requests.post(
            URL,
            data=image_bytes,
                headers={
                "Content-Type": "application/octet-stream",
                "Dwell-Time": DWELL_TIME,
                "Zone": ZONE,
                "Frequency": FREQUENCY
            }

        )

        # 4. Print the JSON response
        print(f"\n[RESPONSE] Status Code: {response.status_code}")
        print("[RESPONSE] Body:")
        print(json.dumps(response.json(), indent=4))

    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server.")
        print("        Make sure backend/app.py is running on http://127.0.0.1:5000")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")


if __name__ == "__main__":
    test_upload()
