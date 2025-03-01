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
My first step was reading the [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction) via the inspector tool to see which HTML attributes were common for the job posting titles. The class "jss-g90" corresponded to each job title:

```html
<a class="jss-g90" href="/careers/45>Job Title</a>
```

I then evaluated the raw HTML from bs4, and using a simple `CMD + F` with the search term "Job Title," I quickly discovered that the webpage actually dynamically loads job postings. Onto [Selenium](https://selenium-python.readthedocs.io/)!

