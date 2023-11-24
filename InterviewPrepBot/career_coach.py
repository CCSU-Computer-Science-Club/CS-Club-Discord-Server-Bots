from CSBotCommon import PalmApi
from CSBotCommon import Bot
from Profanity_Checker import Hand_profanity
import dotenv
import os

dotenv.load_dotenv()
bot = Bot(os.getenv('bot_key'))

import signal
def handle_interrupt(signum, frame):
    print("<bot name> Bot Terminating...")
    bot.botClient.close()
    exit(0)
signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)

@bot.botClient.event
async def on_ready():
    await bot.botClient.tree.sync()
    print(f'The bot has been started!')


@bot.botClient.event
async def on_message(message):
    if bot.botClient.user.mentioned_in(message):
        message_text = message.content.replace("<@1162473601564414022>", "")
        prompt = None

        if message_text:
            user_id =  bot.botClient.get_user(int(os.getenv('discord_user_id')))
            handle =Hand_profanity(user_id, message_text).is_it_bad_word()
            # if No bad words was found in user message, Proceed
            if handle != True: 
            
                prompt = f"""
    You are a dedicated career coach, assisting college students with various aspects of their professional journey,
    including resume refinement, interview preparation, and tailored career advice. Your expertise empowers them to make confident strides in their chosen fields.
    Guidelines:
    - Ensure your response stays within 300 words.
    - Address the student's specific inquiry: {message_text}
    - If you do not get a prompt from the user, just respond to the user stating your purpose and who you are.
    - Do not include links.
    - Only reply to the student to the user's question otherwise !!
    Now, let's craft a thoughtful and impactful response to guide them on their career path.
    """
            else:
                prompt = """
    Hey there! I'm a career coach here to help you navigate your professional journey. Ask me anything about resumes, interviews, career choices, or anything else that's on your mind.
    """
            if prompt:
                try:
                    palmAi = PalmApi("", os.getenv('palm_api_key'))
                    palmAi.prompt = prompt
                    response_from_bot = palmAi.text_generator_agent()
                except:
                    sad='\U0001f63f'
                    response_from_bot = f'Hello, I am sorry I have let you down. I was unable to generate a response for you please try again later {sad}'


                await message.channel.send(f'{response_from_bot}, {message.author.mention}!')
            else:
                return

    await bot.botClient.process_commands(message)


bot.run()
