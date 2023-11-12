### CS-Club-Discord-Server-Bots: Coding Challenger Bot

This folder should contain files related to the CodingChallenger Bot and only this Bot. Some of the files from this folder may call or refer to files outside this folder.

#### Dependencies

- python3.11
- discord.py ==1.7.3 (version requires intents, but for now let just use this version)

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

### Run the bot

run the bot.py file

```bash
python bot.py
```

in discord you can now use the `/challenge` command to get a challenge
