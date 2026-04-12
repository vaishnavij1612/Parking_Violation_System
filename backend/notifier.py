import requests

# Configuration
# Provided Token: 8347226166:AAEl3ZfUMBzIqH9WX0I58MD_qpLGR76Tp4Q
TELEGRAM_BOT_TOKEN = "8347226166:AAEl3ZfUMBzIqH9WX0I58MD_qpLGR76Tp4Q"

# Owners' Chat IDs
# Number 1 & 2: 5648493767 (Single account for now)
CHAT_IDS = [
    "5648493767"
]

def send_telegram_notification(plate, fine, severity):
    """
    Sends a Telegram notification to the configured chat IDs.
    """
    if not TELEGRAM_BOT_TOKEN or "REPLACE_WITH" in str(CHAT_IDS):
        print("[NOTIFIER] Skipping notification: Placeholder used or token missing.")
        return False

    message = (
        f"🚨 *Parking Violation Detected!*\n\n"
        f"🚗 *Vehicle Number:* {plate}\n"
        f"💰 *Fine Amount:* ₹{fine}\n"
        f"⚠️ *Violation Severity:* {severity.upper()}\n\n"
        f"Please visit the dashboard to view details and settle the fine."
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    success = True
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"[NOTIFIER] Failed to send to {chat_id}: {response.text}")
                success = False
            else:
                print(f"[NOTIFIER] Notification sent successfully to {chat_id}")
        except Exception as e:
            print(f"[NOTIFIER] Error sending message: {e}")
            success = False
            
    return success

if __name__ == "__main__":
    # Test script if run directly
    print("Testing Notification with placeholders...")
    send_telegram_notification("TN01AB1234", 500, "High")
