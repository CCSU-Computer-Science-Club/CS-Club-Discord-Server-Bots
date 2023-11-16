import os
import sys
from dotenv import load_dotenv
load_dotenv()

from CSBotCommon import Bot

bot = Bot(os.getenv('bot_token'))

@bot.botClient.event
async def on_ready():
    await bot.botClient.tree.sync()
    print(f'The bot has been started!')

bot.run()