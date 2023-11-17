from CSBotCommon import PalmApi
from CSBotCommon import Bot
import dotenv
import os

dotenv.load_dotenv()
bot = Bot(os.getenv('bot_key'))

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

    await bot.botClient.process_commands(message)


bot.run()
