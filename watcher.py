import os
import time
import requests
import shutil

# --- Configuration ---
WATCH_DIR      = "input_images"
PROCESSED_DIR  = "processed_images"
FAILED_DIR     = "failed_images"
UPLOAD_URL     = "http://127.0.0.1:5000/upload"
DWELL_TIME     = "15"  # Default dwell time in seconds
POLL_INTERVAL  = 3     # Seconds between folder checks

# Ensure directories exist
os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(FAILED_DIR, exist_ok=True)

def process_file(filename):
    filepath = os.path.join(WATCH_DIR, filename)
    
    # Wait a moment to ensure the file is fully copied/written
    time.sleep(1)
    
    print(f"[WATCHER] Processing: {filename}")
    
    try:
        with open(filepath, "rb") as f:
            image_bytes = f.read()

        response = requests.post(
            UPLOAD_URL,
            data=image_bytes,
            headers={
                "Content-Type": "application/octet-stream",
                "Dwell-Time": DWELL_TIME
            }
        )

        if response.status_code == 200:
            print(f"[WATCHER] Success: {filename} -> Dashboard updated.")
            shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
        else:
            print(f"[WATCHER] Failed (HTTP {response.status_code}): {response.text}")
            shutil.move(filepath, os.path.join(FAILED_DIR, filename))

    except requests.exceptions.ConnectionError:
        print("[WATCHER] Error: Could not connect to server. Is the Flask app running?")
    except Exception as e:
        print(f"[WATCHER] Error processing {filename}: {str(e)}")
        # Move to failed to avoid infinite loop on bad files
        if os.path.exists(filepath):
            shutil.move(filepath, os.path.join(FAILED_DIR, filename))

def start_watching():
    print(f"============================================")
    print(f"   Image Watcher Started")
    print(f"   Monitoring: {os.path.abspath(WATCH_DIR)}")
    print(f"============================================")
    
    while True:
        try:
            files = [f for f in os.listdir(WATCH_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for filename in files:
                process_file(filename)
                
        except Exception as e:
            print(f"[WATCHER] Main loop error: {e}")
            
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    start_watching()
