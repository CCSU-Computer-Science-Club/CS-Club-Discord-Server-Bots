### CS-Club-Discord-Server-Bots: Coding Challenger Bot

This folder should contain files related to the CodingChallenger Bot and only this Bot. Some of the files from this folder may call or refer to files outside this folder.

# How to run

### Create .env file

rename the .env.example file in the root folder of the bot

In this file copy the channel ID from discord of the channel you would like the bot to create channel threads in. You can look up how copy the channel ID online, it is quite simple

**Make sure to add a bot token in the .env file**

### Install dependencies

run the command below to install the dependencies, you can do this in a python virtual environment if you so choose

```bash
pip install -r requirements.txt
```

### Setup Docker

The best way to setup docker is to install docker desktop

```
https://www.docker.com/products/docker-desktop/
```

Once docker desktop is installed you will want to run the docker build script associated with your operating system, `dockerBuild.bat` for **windows** and `dockerBuild.sh` for **linux.** These scripts will build the docker images for each of the code validators and will add them to your docker instance.

#### What is docker? Basic Overview

Docker images are virtual machines that are created programatically from a "dockerfile". You can create a container from this docker image. The container will act as its own virtual machine seperate from other containers on your system. You can create multiple containers from the same image if you wish. The docker image acts only as a base from which the container can run and manipilate. Docker allows the bot to run code in sandboxed environments where malicious code will have much much more difficulty causing problems.

### Run the bot

run the bot.py file

```bash
python bot.py
```

in discord you can now use the `/challenge` command to get a challenge
