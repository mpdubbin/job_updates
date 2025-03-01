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
  a. Run the script at a scheduled interval (every 10 minutes? As to not overwhelm the small company system?)  
  b. Scrape the latest job listings.  
 
3. Compare Old and New Job Lists  
  a. Load the previous job list from initial_list.txt.  
  b. Compare the current job list with the previously saved list.    
    i. If no changes → do nothing; exit or wait until the next scheduled run.  
    ii. If new jobs are found → take action    
      - Save the updated job list to a timestamped file, for example: `list_2025-03-01_12-30-00.txt`  
      - Send a notification (email?)



