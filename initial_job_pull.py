from functions import get_job_listings, save_jobs
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("URL")
initial_file_name = "initial_list.txt"

if __name__ == "__main__":
    jobs_list = get_job_listings(url)
    save_jobs(jobs_list, initial_file_name)