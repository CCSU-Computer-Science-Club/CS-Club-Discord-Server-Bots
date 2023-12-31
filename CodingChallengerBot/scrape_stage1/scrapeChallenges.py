from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import json
import time
import pymongo
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
load_dotenv()

options = webdriver.ChromeOptions()
# options.add_argument('--headless')

# Initialises mongodb database that stores challenges
client = pymongo.MongoClient(os.getenv('mongo_string'))
database = client.get_database("CodingChallengeBot")
collection = database.get_collection("Challenges")

# Fetches a challenge from the codewars API if it is not already
# contained in the database
def process_challenge(count, id):
    if not collection.find_one({"_id": id}):
        r = requests.get("https://www.codewars.com/api/v1/code-challenges/" + id)
        print(f"{r.status_code} : {count}")
        if (r.status_code == 429):
            time.sleep(30)
            process_challenge(count, id)
            return

        json_obj = json.loads(r.text)

        #Removes debugging challenges 
        if "Debugging" in json_obj["tags"]:
            return

        json_obj["_id"] = json_obj.pop("id")
        json_obj["difficulty"] = 8 - ((json_obj.pop("rank")["id"] * -1) - 1)
        collection.insert_one(json_obj)


# Fetches and scrapes challenge IDs with a set difficulty
def fetch_by_difficulty(difficulty):
    browser = webdriver.Chrome(options=options)
    browser.get(f'https://www.codewars.com/kata/search/?q=&r%5B%5D=-{difficulty}&beta=false&order_by=popularity%20desc')

    check_limit = 100
    
    for i in range(100):
        # Finds the body of the DOM
        body = browser.find_element(By.ID,"code_challenges")

        # Finds the container that lists the challenges
        container = browser.find_element(By.CSS_SELECTOR,".w-full.md\\:w-9\\/12.md\\:pl-4.pr-0.space-y-4")
        height = container.size["height"]

        # Scrolls to bottom of page
        body.send_keys(Keys.END)
        checks = 0
        # Waits for challenges at the bottom of the page to load
        while(height >= container.size["height"] and checks < check_limit):
            time.sleep(.05)
            checks+=1
        if (checks == check_limit):
            break

    # Find and pull the challenge IDs from the ID html attribute
    parent = browser.find_elements(By.CSS_SELECTOR, "#shell_content > section.items-list.flex.flex-col.md\\:flex-row.max-w-screen-2xl.mx-auto > div.w-full.md\\:w-9\\/12.md\\:pl-4.pr-0.space-y-4")[0]
    child_elements = parent.find_elements(By.CSS_SELECTOR, ".list-item-kata.bg-ui-section.p-4.rounded-lg.shadow-md")

    challenge_ids = []
    for element in child_elements:
        challenge_ids.append(element.get_attribute("id"))

    browser.quit()
    print(str(len(child_elements)) + f" IDs have been scraped - Difficulty: {difficulty}")

    num_threads = 1

    # Able to process the fetched IDs in parallel however due to
    # Rate limiting this is not reccomened 
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda args: process_challenge(*args), enumerate(challenge_ids))

print("Starting...")
with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(fetch_by_difficulty, range(1,9))

# Close mongodb connection 
client.close()
