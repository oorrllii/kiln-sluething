import requests
import csv
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Public CSV URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStXzjItUJ1rP62q1B6yUpUAUKxfpFQV5goc1516fGjyhKCUaO_gxCihHM1Y_TcvzRc3L7zHH6ofmDr/pub?output=csv"

# State file
STATE_FILE = "last_status.txt"

def fetch_data():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    rows = list(csv.reader(response.text.splitlines()))
    return rows

def read_last_status():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_status(status):
    with open(STATE_FILE, "w") as f:
        f.write(status)

def send_email(transition_time, unload_date):
    sender = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    recipient = os.environ["EMAIL_TO"]

    subject = "🔥 Glaze Kiln is Cooling!"
    body = f"""
    The San Francisco glaze kiln transitioned to "Glaze – cooling".

    Transition time: {transition_time}
    Expected unload date: {unload_date}

    Happy firing!
    """

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

def main():
    rows = fetch_data()

    # Assume kiln name is column 0, status is column 1, unload date is column 2
    for row in rows:
        if len(row) < 3:
            continue
        kiln, status, unload_date = row[0], row[1], row[2]

        if True:
            last_status = read_last_status()
            if status != last_status:
                transition_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_email(transition_time, unload_date)
                write_last_status(status)

if __name__ == "__main__":
    main()
