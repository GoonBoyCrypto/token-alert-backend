from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configurations
API_URL = "https://api.dexscreener.io/latest/dex"  # Example DexScreener API
ALERT_CRITERIA = {
    "liquidity": 20000,  # Minimum liquidity threshold
    "days_on_list": 3    # Minimum consecutive days on trending list
}
SUBSCRIBERS = []  # List to store subscriber emails

# Function to fetch token data
def fetch_token_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data")
        return None

# Function to filter tokens based on criteria
def filter_tokens(tokens):
    filtered = []
    for token in tokens:
        if token['liquidity'] >= ALERT_CRITERIA['liquidity']:
            filtered.append(token)
    return filtered

# Function to send email alerts
def send_email_alert(subscribers, tokens):
    smtp_server = "smtp.example.com"  # Replace with your SMTP server
    smtp_port = 587  # Typically 587 for TLS
    smtp_user = "your_email@example.com"
    smtp_password = "your_password"

    for email in subscribers:
        message = MIMEText(f"Alert! The following tokens meet your criteria:\n\n{tokens}")
        message['Subject'] = "Token Alert Notification"
        message['From'] = smtp_user
        message['To'] = email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, email, message.as_string())

# Scheduler to run periodic checks
def check_and_alert():
    data = fetch_token_data()
    if data:
        filtered_tokens = filter_tokens(data.get('pairs', []))
        if filtered_tokens:
            send_email_alert(SUBSCRIBERS, filtered_tokens)

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_and_alert, trigger="interval", hours=1)
scheduler.start()

# Route to add subscribers
@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.json.get('email')
    if email and email not in SUBSCRIBERS:
        SUBSCRIBERS.append(email)
        return jsonify({"message": "Subscribed successfully!"}), 200
    return jsonify({"message": "Invalid or duplicate email."}), 400

# Route to list subscribers (admin/debugging purpose)
@app.route('/subscribers', methods=['GET'])
def get_subscribers():
    return jsonify(SUBSCRIBERS), 200

if __name__ == '__main__':
    app.run(debug=True)
