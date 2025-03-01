import os
import pickle
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None
    print("Checking for existing credentials...")

    # Check if token exists
    if os.path.exists("token.pickle"):
        print("Found token.pickle. Loading credentials...")
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        print("No valid credentials found. Authenticating...")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing credentials...")
            creds.refresh(Request())
        else:
            print("Opening browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
        print("Credentials saved.")

    return creds

if __name__ == "__main__":
    authenticate_gmail()
    print("Authentication complete!")
