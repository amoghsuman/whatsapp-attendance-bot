from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

app = Flask(__name__)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Attendance Sheet").sheet1

# State management for each user
user_state = {}

@app.route("/bot", methods=["GET", "POST"])
def bot():
    if request.method == "GET":
        return "👋 This endpoint is live and waiting for POST messages from Twilio!"
    
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    # Initialize user if not tracked
    if from_number not in user_state:
        user_state[from_number] = {"stage": "ask_name"}
        msg.body("👋 Hello! What's your name?")
        return str(resp)

    user_data = user_state[from_number]

    if user_data["stage"] == "ask_name":
        user_data["name"] = incoming_msg
        user_data["stage"] = "ask_task"
        msg.body("📋 Great, {}. What task did you complete today?".format(user_data["name"]))
    
    elif user_data["stage"] == "ask_task":
        user_data["task"] = incoming_msg
        user_data["stage"] = "ask_hours"
        msg.body("⏱️ And how many hours did you work on this task?")
    
    elif user_data["stage"] == "ask_hours":
        user_data["hours"] = incoming_msg
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log the response in the sheet
        sheet.append_row([
            from_number,
            timestamp,
            user_data["name"],
            user_data["task"],
            user_data["hours"]
        ])
        
        msg.body("✅ Thanks, {}! Your report has been logged.".format(user_data["name"]))
        # Clear state for next entry
        del user_state[from_number]

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
