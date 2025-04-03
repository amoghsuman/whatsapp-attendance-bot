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

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg.lower() in ['hi', 'hello']:
        msg.body("👋 Hello! Please reply with your work summary for today.")
    else:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([from_number, timestamp, incoming_msg])
        msg.body("✅ Thanks! Your summary has been recorded.")
    
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
