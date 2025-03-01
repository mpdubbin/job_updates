import base64
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from gmail_auth import authenticate_gmail 

# Load environment variables
load_dotenv()
my_email = os.getenv("MY_EMAIL")


def send_email(to, subject, body):
    """Send an email using Gmail API."""
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    # Create the email
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"raw": raw_message}

    try:
        sent_message = service.users().messages().send(userId="me", body=body).execute()
        print(f"Email sent! Message ID: {sent_message['id']}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example usage
send_email(my_email, "Hello from Python!", "This is a test email sent via Gmail API with OAuth2.")
