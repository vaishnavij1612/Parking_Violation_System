import requests
import json

TOKEN = "8347226166:AAEl3ZfUMBzIqH9WX0I58MD_qpLGR76Tp4Q"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

def get_recent_chat_ids():
    try:
        response = requests.get(URL)
        data = response.json()
        
        if not data.get("ok"):
            print(f"Error: {data.get('description')}")
            return
            
        updates = data.get("result", [])
        if not updates:
            print("No recent messages found. Ask the person to send a message to the bot now.")
            return

        print("\n--- Recent Chat IDs ---")
        seen = set()
        for update in updates:
            chat = None
            if "message" in update:
                chat = update["message"]["chat"]
            elif "my_chat_member" in update:
                chat = update["my_chat_member"]["chat"]
            
            if chat:
                chat_id = str(chat["id"])
                first_name = chat.get("first_name", "Unknown")
                username = chat.get("username", "N/A")
                
                if chat_id not in seen:
                    print(f"ID: {chat_id} | Name: {first_name} | Username: @{username}")
                    seen.add(chat_id)
        print("-----------------------\n")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    get_recent_chat_ids()
