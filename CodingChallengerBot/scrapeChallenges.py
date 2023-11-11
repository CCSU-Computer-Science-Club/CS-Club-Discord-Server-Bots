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
#options.add_argument('--headless')

client = pymongo.MongoClient(os.getenv('mongo_string'))
database = client.get_database("CodingChallengeBot")
collection = database.get_collection("Challenges")

def process_challenge(count, id):
    if not collection.find_one({"_id": id}):
        r = requests.get("https://www.codewars.com/api/v1/code-challenges/" + id)
        print(f"{r.status_code} : {count}")
        if (r.status_code == 429):
            time.sleep(30)
            process_challenge(count, id)
            return

        json_obj = json.loads(r.text)

        if "Debugging" in json_obj["tags"]:
            return

        json_obj["_id"] = json_obj.pop("id")
        json_obj["difficulty"] = 8 - ((json_obj.pop("rank")["id"] * -1) - 1)
        collection.insert_one(json_obj)

def fetch_by_difficulty(difficulty):
    browser = webdriver.Chrome(options=options)
    browser.get(f'https://www.codewars.com/kata/search/?q=&r%5B%5D=-{difficulty}&beta=false&order_by=popularity%20desc')

    check_limit = 100
    
    for i in range(100):
        body = browser.find_element(By.ID,"code_challenges")
        container = browser.find_element(By.CSS_SELECTOR,".w-full.md\\:w-9\\/12.md\\:pl-4.pr-0.space-y-4")
        height = container.size["height"]
        body.send_keys(Keys.END)
        checks = 0
        while(height >= container.size["height"] and checks < check_limit):
            time.sleep(.05)
            checks+=1
        if (checks == check_limit):
            break


    parent = browser.find_elements(By.CSS_SELECTOR, "#shell_content > section.items-list.flex.flex-col.md\\:flex-row.max-w-screen-2xl.mx-auto > div.w-full.md\\:w-9\\/12.md\\:pl-4.pr-0.space-y-4")[0]
    child_elements = parent.find_elements(By.CSS_SELECTOR, ".list-item-kata.bg-ui-section.p-4.rounded-lg.shadow-md")

    challenge_ids = ["64fc00392b610b1901ff0f17"]
    for element in child_elements:
        challenge_ids.append(element.get_attribute("id"))

    browser.quit()
    print(str(len(child_elements)) + f" IDs have been scraped - Difficulty: {difficulty}")

    num_threads = 1

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda args: process_challenge(*args), enumerate(challenge_ids))

print("Starting...")
with ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(fetch_by_difficulty, range(1,9))



client.close()
