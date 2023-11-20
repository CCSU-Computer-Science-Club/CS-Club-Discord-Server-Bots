### CS-Club-Discord-Server-Bots: Common Files

This folder should contain files that are used in more than one bots.
Classes or Function that bots have in common should be added to this folder.

### CSBot.py - Class Implementation and use

The CSBot class is used as a starting point for any bots created in this codebase and acts as a framework that can be expanded as needed. Because this class is common across all bots sharing functionality is much simpler

#### Instantiating an object of the CSBot class example

Below shows an example implementation of a very simple bot created using the CSBot class

```python
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from CSBotCommon import Bot

bot = Bot(os.getenv('mongo_string'), os.getenv('bot_token'))

@bot.botClient.event
async def on_ready():
    await bot.botClient.tree.sync()
    print(f'The bot has been started!')

bot.run()
```
