import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


async def findJobs(location):
    urls = {
        'middletown': 'https://www.indeed.com/jobs?q=software+internship&l=Middletown%2C+CT&radius=25',
        'waterbury': 'https://www.indeed.com/jobs?q=software+internship&l=Waterbury,+CT&radius=25',
        'newhaven': 'https://www.indeed.com/jobs?q=software+internship&l=New+Haven,+CT&radius=25',
        'stamford': 'https://www.indeed.com/jobs?q=software+internship&l=Stamford,+CT&radius=25',
        'hartford': 'https://www.indeed.com/jobs?q=software+internship&l=Hartford,+CT&radius=25'
    }
    selected_url = urls.get(location)

    loop = asyncio.get_event_loop()
    job_titles = await loop.run_in_executor(None, lambda: scrapeJobs(selected_url))
    return job_titles

def scrapeJobs(selected_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options = chrome_options)
    driver.get(selected_url)

    numScrolls = 1
    for i in range(numScrolls):
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(5)
    jobs = driver.find_elements(By.CLASS_NAME, 'job_seen_beacon')
    print(len(jobs))
    alljobs = []

    for job in jobs:
        title = job.find_element(By.CSS_SELECTOR, 'h2.jobTitle > a').text
        moreInfo = job.find_element(By.CSS_SELECTOR, 'h2.jobTitle > a').get_attribute('href')
        alljobs.append((title, moreInfo))

    driver.quit()
    return alljobs

