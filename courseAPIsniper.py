import time
import requests
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Define the sections you're monitoring
desired_sections = {"08664", "22354", "21942", "11742"}

# API endpoint
api_url = "https://classes.rutgers.edu/soc/api/openSections.json?year=2025&term=1&campus=NB"

load_dotenv(dotenv_path=r"C:\Users\aaron\course_sniper\secrets.env")

# Track previously notified open sections
email_user = os.getenv('EMAIL_USER')
email_pass = os.getenv('EMAIL_PASS')

def get_open_sections():
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return set(response.json())  # Assume the API returns a list of open section IDs
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return set()

def sendSMS(subject, message, phone_number, carrier_email):
    from_email = email_user
    to_email = f"{phone_number}@{carrier_email}"  # e.g., "1234567890@vtext.com"
    password = email_pass

    # Create the message
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
            print(f"Message sent to {phone_number}")
    except Exception as e:
        print(f"Error sending message: {e}")

try:
    while desired_sections:  # Continue only while there are desired sections to check
        open_sections = get_open_sections()
        
        # Find open sections that are in the desired list
        open_desired_sections = desired_sections & open_sections
        
        if open_desired_sections:
            number = 6104579946
            carrier = "vtext.com"
            for course in open_desired_sections:
                message = f"{course} is now open!\nRegister: https://sims.rutgers.edu/webreg/%20editSchedule.htm?%20login=cas&semesterSelection=12025&indexList={course}"
                sendSMS("Sections Opened", message, number,carrier)

            # Remove the found sections from the desired list
            desired_sections -= open_desired_sections
        
        # Wait for 5 seconds before checking again
        time.sleep(5)

    print("All desired sections have been found!")
except KeyboardInterrupt:
    print("Stopped checking for open sections.")