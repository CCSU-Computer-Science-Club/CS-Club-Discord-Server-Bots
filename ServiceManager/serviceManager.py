import requests
import os
import sys
import subprocess
import time
import signal
import json
import platform
from dotenv import load_dotenv
load_dotenv()

# Load the config
if (not os.path.exists("service.json")):
    print("service.json file not found")
    exit(1)

config = json.loads(open("service.json", "r").read())

python_exec = config["pythonPath"]

currentCommit = ""
if os.path.exists("latestCommit.txt"):
    with open("latestCommit.txt", "r") as file:
        currentCommit = file.read()

running_processes = []
def startProcesses():
    for service in config["services"]:
        #process = subprocess.Popen(['python', arg])
        process = subprocess.Popen([python_exec, service])
        running_processes.append(process)


def getLatestCommit(username, repo_name):
    url = f'https://api.github.com/repos/{username}/{repo_name}/branches/main'
    headers = {"Authorization": f"Bearer {os.getenv('github_token')}"}

    response = requests.get(url, headers=headers)
    branch_info = response.json()
    last_commit_sha = branch_info['commit']['sha']
    return last_commit_sha

def invokeUpdate():
    for p in running_processes:
        p.terminate()
    subprocess.run("git pull origin main")
    for script in config["updateScripts"]:
        if platform.system() == 'Windows':
            subprocess.run([script])
        elif platform.system() == 'Linux':
            subprocess.run(['bash', script])
    startProcesses()

def handle_interrupt(signum, frame):
    print("Terminating Processes...")
    for p in running_processes:
        p.terminate()
    exit(0)
signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)


startProcesses()
while True:
    print("Running update check...")
    username = 'CCSU-Computer-Science-Club'
    repo_name = 'CS-Club-Discord-Server-Bots'

    latestCommit = getLatestCommit(username, repo_name)

    if currentCommit != latestCommit:
        currentCommit = latestCommit
        invokeUpdate()
        print("Update found...")

    with open("latestCommit.txt", "w") as file:
        file.write(latestCommit)
    time.sleep(10)