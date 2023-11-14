import os
import sys
from dotenv import load_dotenv
load_dotenv()

from ..Common.CSBot import CSBot

bot = CSBot(os.getenv('mongo_string'), os.getenv('bot_token'))

bot.run()