import discord
from discord.ext import commands
from discord import ChannelType
from discord import app_commands
import subprocess
import docker
import pymongo
import os
import random
import re
import signal
from CSBotCommon import Bot
import time
import shutil
from codeValidator import validateCode
from dotenv import load_dotenv
load_dotenv()


# Channel threads will be created in
challenge_channel_id = os.getenv("challenge_channel_id")
active_challenges = {}

bot_instance = Bot(os.getenv('bot_token'), mongoUri=os.getenv('mongo_string'))
client = bot_instance.botClient

# Allows for clean termination
def handle_interrupt(signum, frame):
    print("Coding Challenger Bot Terminating...")
    bot_instance.botClient.close()
    exit(0)
signal.signal(signal.SIGINT, handle_interrupt)
signal.signal(signal.SIGTERM, handle_interrupt)


# Initialises mongodb database that stores challenges
db_client = bot_instance.mongoClient
database = db_client.get_database("CodingChallengeBot")
collection = database.get_collection("Challenges")
users_collection = database.get_collection("Users")


# Start the discord bot
@client.event
async def on_ready():
    commands = await client.tree.sync()
    print(f'{len(commands)} command(s) synced')


def parseResult(result:str):
    lines:list[str] = result.split("\n")
   

    if result.startswith("<SYSTEM::>"):
        return result.replace("<SYSTEM::>", ""), 0.0, True
    
    parsed_output = []
    for line in lines:
        if line == "":
            continue
        prefix, content = line.split("::>")
        if prefix == "<DESCRIBE":
            parsed_output.append(content.strip())
        elif prefix == "<IT":
            current_test = content.strip()
            parsed_output.append(f"᲼᲼{current_test}")
        elif prefix == "<FAILED":
            parsed_output.append(f"᲼᲼᲼᲼**Failed**:\n᲼᲼᲼᲼᲼᲼{content.strip()}")
        elif prefix == "<PASSED":
            parsed_output.append(f"᲼᲼᲼᲼**Passed**:\n᲼᲼᲼᲼᲼᲼{content.strip()}")
    lines.reverse()
    for line in lines:
        if line.startswith("<COMPLETEDIN::>"):
            completed_in = float(line.removeprefix("<COMPLETEDIN::>"))
            break

    return "\n".join(parsed_output), completed_in, False


class SubmitSolutionModal(discord.ui.Modal, title='Submit Solution'):
    soulution = discord.ui.TextInput(
        label='Paste your solution here',
        style=discord.TextStyle.long,
        placeholder='print("Hello World!")',
        required=True,
    )
    def remainder(a, b):
        if b == 0:
            return None
        return max(a, b) % min(a, b)

    async def on_submit(self, interaction: discord.Interaction):

        filter = {"_id": active_challenges[interaction.channel.id]["id"]}
        lang = active_challenges[interaction.channel.id]["lang"]        
        code_doc = list(collection.find(filter))[0]

        validate_code = code_doc["code"][lang]["exampleFixture"]
        user_code = interaction.data["components"][0]["components"][0]["value"]


        embed=discord.Embed(title="Running code", description=f"Loading...", color=0x1f5ad1)
        embed.set_footer(text="Please wait...")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        result = validateCode(user_code, validate_code, lang)
        embed = None
        passed = False

        if (result == None or result == ""):
            embed=discord.Embed(title="Result", description=result, color=0xcc0000)
        else:
            result, time, error  = parseResult(result)
            if error:
                result = result.replace("\t", "᲼᲼")
                embed=discord.Embed(title="Error", description=result, color=0xcc0000)
            else:
                if ("Failed" in result):
                    embed=discord.Embed(title="Result", description=result, color=0xe69138)
                else:
                    passed = True
                    embed=discord.Embed(title="Result", description=result, color=0x8fce00)

            embed.set_footer(text="Execution time: " + str(time * 1000) + "ms")
        try:
            await interaction.edit_original_response(embed=embed)
        except:
            pass
        if (passed):

            users = list(users_collection.find({"_id": interaction.user.id}))
            user = None
            if (len(users) == 0):
                user = {"_id": interaction.user.id, "score": 0, "completed": []}
                users_collection.insert_one(user)
            else:
                user = users[0]
            id = code_doc["_id"]
            id = id + "-" + lang
            if (id not in user["completed"]):
                user["score"] += code_doc["difficulty"]
                user["completed"].append(id)

                users_collection.replace_one({"_id": interaction.user.id}, user)

                embed=discord.Embed(title="User Statistics", description=f"Challenges Complete: {len(user['completed'])}\nScore: {user['score']}", color=0x1f5ad1)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed=discord.Embed(title="Sorry!", description=f"You have already completed this challenge using {lang}, no more points can be awarded", color=0x1f5ad1)
                await interaction.followup.send(embed=embed, ephemeral=True)
            
        
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        print(error)
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

# Defines button interaction view to close a challenge
# Send as firsy message in the created thread
class ChallengeOptions(discord.ui.View):
    def __init__ (self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Challenge", style=discord.ButtonStyle.danger)
    async def CloseThread(self, interaction:discord.Interaction, button: discord.ui.Button):
        active_challenges.pop(interaction.channel.id)
        await interaction.response.defer()
        await interaction.channel.delete()
    @discord.ui.button(label="Submit Solution", style=discord.ButtonStyle.green)
    async def SubmitSolution(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SubmitSolutionModal())


# Defines slash command auto complete
#langs = ['javascript', 'java', 'csharp', 'python', 'typescript', 'cpp']
langs = ['javascript', 'python', 'typescript']

async def lang_autocomplete(
interaction: discord.Interaction,current: str) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=lang, value=lang) for lang in langs if current.lower() in lang.lower()
    ]
difficulties = ["1", "2", "3", "4", "5", "6", "7", "8", "any"]
async def difficulty_autocomplete(
interaction: discord.Interaction,current: str) -> list[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name=difficulty, value=difficulty) for difficulty in difficulties if current.lower() in difficulty.lower()
    ]

@client.tree.command(name="challenge", description="Test yourself with a coding challenge")
@app_commands.autocomplete(lang=lang_autocomplete)
@app_commands.autocomplete(difficulty=difficulty_autocomplete)
async def challenge(interaction: discord.Interaction, lang: str, difficulty: str = "any", private: bool = False):

    # Command parameter validation
    if (lang not in langs):
        embed=discord.Embed(title="Whoops!", description="**That language is not supported!**", color=0xff0000)
        embed.set_footer(text="Please try again!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    if (difficulty not in difficulties):
        embed=discord.Embed(title="Whoops!", description="**That difficulty is not supported!**", color=0xff0000)
        embed.set_footer(text="Please try again!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Create challenge thread
    threadType = ChannelType.private_thread if private else ChannelType.public_thread
    channel = client.get_channel(int(challenge_channel_id))
    thread = await channel.create_thread(
        name="Loading...",
        type=threadType
    )
    if not private:
        system_message = [message async for message in channel.history(limit=1)][0]
        if "started a thread" in system_message.system_content:
            await system_message.delete()
    await thread.add_user(interaction.user)


    # Respond to command now as mongodb query can be slow and an interaction
    # must be responded to within 3 seconds
    embed=discord.Embed(title="Challenge Started", description=f"Loading...", color=0x1f5ad1)
    embed.set_footer(text="Please wait...")
    await interaction.response.send_message(embed=embed, ephemeral=private)

    # Querey the mongodb database
    filter = {"languages": {"$in": [lang]}}
    if difficulty != "any":
        filter["difficulty"] = int(difficulty)

    docs = list(collection.find(filter))
    doc = docs[random.randint(0, len(docs) - 1)]

    
    # Format and send the challenge to the newly created thread
    embed=discord.Embed(title=doc["name"], description=doc["category"], color=0x1f5ad1)
    embed.add_field(name="Code Wars Link", value=doc["url"], inline=True)
    embed.add_field(name="Difficulty", value=doc["difficulty"], inline=True)
    embed.set_footer(text="Supported Languages: " + " ".join(doc["languages"]))

    content = doc["description"]
    cleaned_content = re.sub(r'<[^<]+?>', '', content)
    cleaned_content= re.sub(r'\n{3,}', '\n\n', cleaned_content)
    cleaned_content.replace("~~~", "")

    result_chunks = bot_instance.break_string_into_chunks(cleaned_content)
    
    await thread.edit(name=doc["name"])
    await thread.send(embed=embed, view=ChallengeOptions())

    for index,chunk in enumerate(result_chunks):
        if (index == 0):
            await thread.send(chunk)
        else:
            await thread.send(chunk)
    
    await thread.send(f"```{lang}\n" + doc["code"][lang]["setup"] + "\n```")

    active_challenges[thread.id] = {"id": doc["_id"], "lang": lang}

    # Update challenge response to show challenge info and link to the thread
    embed=discord.Embed(title="Challenge Started", description=f"View the challenge here: {thread.jump_url}", color=0x1f5ad1)
    embed.add_field(name="Title", value=doc["name"])
    embed.add_field(name="Difficulty", value=doc["difficulty"])
    embed.set_footer(text="Support Languages: " + " ".join(doc["languages"]))
    try:
        await interaction.edit_original_response(embed=embed)
    except:
        pass

@client.tree.command(name="leaderboard", description="View the challenge leaderboard")
async def leaderboard(interaction: discord.Interaction):
    users = list(users_collection.find().sort("passed", -1).limit(10))
    embed=discord.Embed(title="Leaderboard", color=0x1f5ad1)

    result = ""
    for index,user in enumerate(users):
        discord_user = client.get_guild(interaction.guild_id).get_member(user["_id"])
        name = "Unknown"
        if (discord_user != None):
            name = discord_user.nick
            if (name == None):
                name = discord_user.name
        embed.add_field(name="**" + str(index + 1) + ":**" + " " + name, value=f"Score: {user['score']}", inline=False)

    await interaction.response.send_message(embed=embed)

bot_instance.run()