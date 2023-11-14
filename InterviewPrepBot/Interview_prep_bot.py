import discord
from discord.ext import commands
from PalmAi import  hey_bot
import discord
from discord.ext import commands
import dotenv
import os

dotenv.load_dotenv()
bot_key = os.getenv("bot_token")
palm_api_key= os.getenv("palm_api_key")

#client = discord.Client()
#bot = commands.Bot(command_prefix='!')
bot = commands.Bot(command_prefix="||||||", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message): 
    if bot.user.mentioned_in(message):
        message_text = message.content.replace("<@1162473601564414022>", "")
        
        prompt = f""" 
        You are a dedicated career coach, assisting college students with various aspects of their professional journey, 
        including resume refinement, interview preparation, and tailored career advice. Your expertise empowers them to
        make confident strides in their chosen fields.
        
        Guidelines:
        - Ensure your response stays within 300 words.
        - Address the student's specific inquiry: {message_text}
        - Do not include Links.
        - Only reply to the student to the user question otherwise !!
        Now, let's craft a thoughtful and impactful response to guide them on their career path.
        
        """
       
        response_from_bot = hey_bot(prompt)
        await message.channel.send(f'{response_from_bot}, {message.author.mention}!')
        

    await bot.process_commands(message)


bot.run(bot_key)

