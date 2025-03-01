# All you have to do is run this script
# It first runs the initial_job_pull.py once to populate the initial .txt file
# It then, through scheduling, periodically pulls the jobs from the webpage, checks for changes, and sends a notification if a change occurs

import schedule
import time
from dotenv import load_dotenv
from functions import *

# Load environment variables
load_dotenv()
url = os.getenv("URL")

# Run function immediately to pull job list
check_for_updates()

# Schedule check_for_updates() to run every 10 minutes
schedule.every(5).minutes.do(check_for_updates)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
