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
process_loop = True

currentCommit = ""
if os.path.exists("latestCommit.txt"):
    with open("latestCommit.txt", "r") as file:
        currentCommit = file.read()

running_processes = []
process_commands = []
def startProcesses():
    global running_processes, process_commands
    running_processes = []
    process_commands = []
    for service in config["services"]:
        #process = subprocess.Popen(['python', arg])
        process = subprocess.Popen([python_exec, service])
        running_processes.append(process)
        process_commands.append([python_exec, service])


def getLatestCommit(username, repo_name):
    url = f'https://api.github.com/repos/{username}/{repo_name}/branches/main'
    headers = {"Authorization": f"Bearer {os.getenv('github_token')}"}

    try:
        response = requests.get(url, headers=headers)
        if (response.status_code != 200):
            return currentCommit
        branch_info = response.json()
        last_commit_sha = branch_info['commit']['sha']
        return last_commit_sha
    except:
        return currentCommit

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
    global process_loop
    print("Terminating Processes...")
    process_loop = False
    for p in running_processes:
        p.terminate()
    exit(0)
signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)


startProcesses()
while process_loop:
    username = 'CCSU-Computer-Science-Club'
    repo_name = 'CS-Club-Discord-Server-Bots'

    latestCommit = getLatestCommit(username, repo_name)

    if currentCommit != latestCommit:
        print("Update found...")
        with open("latestCommit.txt", "w") as file:
            file.write(latestCommit)
        currentCommit = latestCommit
        invokeUpdate()
    else:
        for index,p in enumerate(running_processes):
            if (p.poll() is not None):
                print("Reviving process: " + p.args[1])
                process = subprocess.Popen(process_commands[index])
                running_processes[index] = process
    time.sleep(10)