# CS-Club-Discord-Server-Bots

Computer Science Club Discord Server Bots

## Configuration

### `service.json`

The service manager relies on a configuration file named `service.json`. This file defines the services to be managed, the Python interpreter path, and update scripts to be executed after pulling changes from the GitHub repository.

Example `service.json`:

```json
{
  "pythonPath": "/path/to/python/interpreter",
  "services": ["service1.py", "service2.py"],
  "updateScripts": ["update_script1.sh", "update_script2.sh"]
}
```

* `pythonPath`: Path to the Python interpreter executable.
* `services`: List of service scripts to be managed.
* `updateScripts`: List of scripts to be executed after updating from the GitHub repository.

## Service Manager Logic

1. **Configuration Loading:**
   * The script starts by loading the configuration from `service.json`.
   * It reads the Python interpreter path, service scripts, and update scripts.
2. **GitHub Token:**
   * The script checks for the presence of a GitHub token in the `.env` file.
   * The GitHub token is used for API authentication when querying the repository.
3. **Service Startup:**
   * The script starts the specified services as separate subprocesses.
   * The processes are stored in the `running_processes` list for later management.
4. **Update Check Loop:**
   * The script enters an infinite loop to periodically check for updates.
   * It queries the GitHub repository to get the latest commit in the main branch.
5. **Update Detection:**
   * If a new commit is detected, the script terminates the running services.
   * It then pulls the latest changes from the GitHub repository and executes update scripts.
6. **Service Restart:**
   * After updates are applied, the script restarts the services with the new code.
7. **Update Commit Tracking:**
   * The latest commit is recorded in a file (`latestCommit.txt`) to track changes.
8. **Sleep Interval:**
   * The script sleeps for a specified interval (10 seconds by default) before checking for updates again.
9. **Interrupt Handling:**
   * The script is designed to gracefully terminate the running processes when interrupted (e.g., using Ctrl+C).

# Setup

### Create .env file

rename the .env.example file in the root folder of the bot

In this file copy the channel ID from discord of the channel you would like the bot to create channel threads in. You can look up how copy the channel ID online, it is quite simple

**Make sure to add a bot token in the .env file**

### Install dependencies

run the command below to install the dependencies, you can do this in a python virtual environment if you so choose

```bash
pip install -r requirements.txt
```

#### Installing CSBotCommon Module

`cd` into the directory `CSBotCommon` and run the command

```bash
pip install .
```

This needs to be ran everytime the CSBotCommon module is updated

### Setup Docker

The best way to setup docker is to install docker desktop

```
https://www.docker.com/products/docker-desktop/
```

Once docker or docker desktop is installed you will want to run the docker build script associated with your operating system, `dockerBuild.bat` for **windows** and `dockerBuild.sh` for **linux.** These scripts will build the docker images for each of the code validators and will add them to your docker instance.

#### What is docker? Basic Overview

Docker images are virtual machines that are created programatically from a "dockerfile". You can create a container from this docker image. The container will act as its own virtual machine seperate from other containers on your system. You can create multiple containers from the same image if you wish. The docker image acts only as a base from which the container can run and manipilate. Docker allows the bot to run code in sandboxed environments where malicious code will have much much more difficulty causing problems.
