from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import time

from typing import List


def get_job_listings(url: str) -> List[str]:
    """Use Selenium to extract job titles from the dynamically loaded webpage."""
    
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(url)

        # Wait for job listings to load
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


def save_jobs(jobs: List[str], filename: str) -> None:
    """Save job listings to a file."""
    with open(filename, "w") as file:
        for job in jobs:
            file.write(job + "\n")