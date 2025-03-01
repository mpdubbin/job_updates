# job_updates  

A recruiter reached out to me to apply to a job going live on X date, but without specifying a time.  

Instead of waiting around and actively refreshing the webpage throughout the day, I decided to write a script to notify me when the company's job page updates.

### First thoughts 
1. Use [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/en/latest/) to pull the HTML and appropriate job postings attributes
2. Create a list of the job titles, prior to the posting date, and save to a .txt file 
3. [Cron](https://www.howtogeek.com/devops/what-is-a-cron-job-and-how-do-you-use-them/) job to periodically ping the webpage
4. Check the newly pulled list against the existing .txt file
5. If different, send me a message or notification  

### First pass
My first step was evaluating the raw HTML from bs4. Using a simple `CMD + F` with the search term "Job Title," I quickly discovered that, due to the *absence* of "Job Title" in the requested HTML, the webpage actually dynamically loads job postings. Onto [Selenium](https://selenium-python.readthedocs.io/)!

To begin, I read the [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction) via the inspector tool to see which HTML attributes were common for the job posting titles. The class "jss-g90" corresponded to each job title:

```html
<a class="jss-g90" href="/careers/1">Job Title A</a>
...
<a class="jss-g90" href="/careers/2">Job Title B</a>
```

I then wrote a Python function to pull all of the `a` attributes of class "jss-g90." 

```python
def get_job_listings(url: str) -> List[str]:
    """Use Selenium to extract job titles from the dynamically loaded page."""
    
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        driver.get(url)

        # Wait for job listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jss-g90"))
        )

        # Extract job titles
        job_elements = driver.find_elements(By.CLASS_NAME, "jss-g90")
        job_list = [job.text.strip() for job in job_elements]

    except Exception as e:
        print(f"Error fetching jobs: {e}")
        job_list = []

    finally:
        driver.quit()

    return job_list
```

To my surprise, the returned list was blank. Interesting; did I mistype the class name? I returned to the DOM, searched for "jss-c90," and no matches!

Perhaps the class name changes as some security measure to confuse bots? I refreshed the page - nope, still "jss-g90."

I use Firefox as my primary browser, but Chrome as my Selenium browser - can class names change across browsers? As it turns out, they can; you learn something new every day. The class name in Chrome is "jss-g13," so I ran my script using "jss-g13" and the job postings list was successfully returned.

### Saving to .txt file or hash?
Because this was a first pass, and it was super early on a Saturday morning, and at the time the company site  only had 4 job postings, I decided to simply save the job titles in a .txt file - no need to overengineer. I can update the script when I find another interesting company that I would like to track. Which, for larger companies, the script will have to be updated to account for pagination anyways.

Also, in the email notification step I'd like to see the job title, and that'd be easier to set up using the .txt method.

For either case, the workflow I devised is as follows:

1. Initial Job Pull
  a. Use Selenium to scrape job titles from the careers page.  
  b. Store the job titles as a list called `initial_list.txt`.  

2. Second Job Pull (scheduled execution) (checker_job_pull.py)  
  a. Run the script at a scheduled interval (every 10 minutes? As to not overwhelm the small company system?) (Side note: I was thinking of doing a full CRON job, but not necessary for this little project.) 
  b. Scrape the latest job listings.  
 
3. Compare Old and New Job Lists  
  a. Load the previous job list from initial_list.txt.  
  b. Compare the current job list with the previously saved list.    
    i. If no changes → do nothing; exit or wait until the next scheduled run.  
    ii. If new jobs are found → take action    
      - Save the updated job list to a timestamped file, for example: `list_2025-03-01_12-30-00.txt`  
      - Send a notification (email?)


### Development journey
Moved the Selenium function into its own folder to keep from accidental editing. Created a second function to store the pulled list of jobs into a .txt file (initial_list.txt). That was the easy part - theoretically I could just leave it at that and manually look if there were job updates, but that would require me sitting at my desk all day and running `python main.py` from the terminal every few minutes.

Onto the logic of pulling the webpage's data again and checking for changes against the saved .txt file.

I have:
- function that grabs job listings from the webpage
- function that saves job listings to a .txt file

I need:
- function that reads the saved .txt file
- function that compares the saved .txt file jobs list to the freshly pulled jobs list
- a way to have the pulls and comparison be automatic
- a way to notify me that a new job is up, and the name of that job (in case the job is not relevant to me)

I developed the first function, no problem.

```python
def save_jobs(filename:str) -> None:
    with open(filepath, "w") as file:
        for job in jobs:
            file.write(job + "\n")
```

As I sat back and looked at the function my eyes drifted to the [rubber duck](https://en.wikipedia.org/wiki/Rubber_duck_debugging) perched on my desk. It stared back, unblinking, almost soulless, waiting for me to realize something (as it usually does): this function always writes to the same filename I pass it. For example, if I call it to save the initial job list, it will create the file initial_jobs.txt. 

If I step away from my desk and let the script run a couple of times in my absence, there’s the possibility that initial_jobs.txt gets completely overwritten and any record of changes that happened while I was away vanish (besides the email notification). If an update occurred and disappeared before I checked, I'd have to put in extra effort to see the changes.

I needed a better approach—one that preserves historical data rather than overwriting it. And because the datasets are so small, I decided to create a pseudo-log of history, using the date and time in the file name `list_YYY_MM_DD_HH-MM-SS.txt`. Now I can have my script read the **most recent** file instead of continuously overwriting the initial one. This also allows me to run the script tomorrow and then next day if the recruiter's date was incorrect.

I created a new directory to store the files: `job_lists/`. And updated the save_jobs() function:

```python
def save_jobs(jobs: List[str], filename: str) -> None:
    """Save job listings to a file inside the job_lists/ directory."""
    os.makedirs(JOB_LISTS_DIR, exist_ok=True)

    filepath = os.path.join(JOB_LISTS_DIR, os.path.basename(filename))  

    with open(filepath, "w") as file:
        for job in jobs:
            file.write(job + "\n")
```

I then created two functions: one that finds the most recent file, and one that reads that file. I now had: 
- function that grabs job listings from the webpage
- function that saves job listings to a .txt file
- function that reads the saved .txt file

Up next is to glue it all together: pull data, save data -> pull data, read data, compare to saved data. This took a a few rounds of pseudocode, which resulted in the function `check_for_updates()` in main.py. 

I have done [CRUD](https://database.guide/what-is-crud/) work like this before, and this is a simple example, which behaves as expected. What I haven't done before is...



