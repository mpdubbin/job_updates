import glob
import os
import time
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Environment variables
load_dotenv()
url = os.getenv("URL", "")

# Directory to store job list files
JOB_LISTS_DIR = "job_lists"

# Ensure the job_lists directory exists
os.makedirs(JOB_LISTS_DIR, exist_ok=True)


def get_latest_job_file() -> str:
    """Find the most recent job listing file in the job_lists directory."""
    files = sorted(glob.glob(f"{JOB_LISTS_DIR}/list_*.txt"), reverse=True)
    return files[0] if files else None


def get_job_listings(url: str) -> List[str]:
    """Use Selenium to extract job titles from the dynamically loaded webpage."""
    
    options = Options()
    options.add_argument("--headless") # In case there are popups 

    # Initialize WebDriver
    service = Service(ChromeDriverManager().install()) # If already installed, does not re-install
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        # Wait 10 seconds for job listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jss-g13"))
        )

        # Extract job titles
        job_elements = driver.find_elements(By.CLASS_NAME, "jss-g13")
        job_list = [job.text.strip() for job in job_elements]

    except Exception as e:
        print(f"Error fetching jobs: {e}")
        job_list = []

    finally:
        driver.quit()

    return job_list


def load_previous_jobs() -> List[str]:
    """Load job listings from the most recent file in the job_lists directory."""
    latest_file = get_latest_job_file()
    
    if not latest_file:
        return []

    with open(latest_file, "r") as file:
        return [line.strip() for line in file.readlines()]


def save_jobs(jobs: List[str], filename: str) -> None:
    """Save job listings to a file inside the job_lists/ directory."""
    os.makedirs(JOB_LISTS_DIR, exist_ok=True)  # Ensure the directory exists

    filepath = os.path.join(JOB_LISTS_DIR, os.path.basename(filename)) 

    with open(filepath, "w") as file:
        for job in jobs:
            file.write(job + "\n")
                

def notify(new_jobs: List[str]) -> None:
    """Send a notification (console log for now, but can be email/Discord)."""
    print(f"New jobs detected: {new_jobs}")
    # TODO: Integrate email or text alerts.


def check_for_updates():
    """Compare current job listings with saved ones and take action if different."""
    
    # First pull 
    jobs = get_job_listings(url)  
    
    if not jobs:
        print("No jobs found. Webpage down or moved?")
        return

    # Load previous job listings
    old_jobs = load_previous_jobs()

    # Timestamp for tracking updates
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_file = f"{JOB_LISTS_DIR}/list_{timestamp}.txt"
    
    # First time script runs, just save the list without comparison
    if not old_jobs:
        print(f"Saving initial job list as {new_file}.")
        save_jobs(jobs, new_file)
        return

    # Compare job listings
    if set(jobs) == set(old_jobs):
        print("No new jobs detected. Waiting for next run.")
        return

    # If different, save the updated job list with a timestamp
    save_jobs(jobs, new_file)
    
    # Notify about new jobs
    new_jobs = list(set(jobs) - set(old_jobs))
    if new_jobs:
        notify(new_jobs)

    print(f"New job list saved as {new_file}.")