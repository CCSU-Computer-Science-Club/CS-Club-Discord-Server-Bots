import discord
from discord.ext import commands
from discord import ChannelType
from discord import app_commands

import pymongo
import os
import random
import re
from dotenv import load_dotenv
load_dotenv()

client = pymongo.MongoClient(os.getenv('mongo_string'))
database = client.get_database("CodingChallengeBot")
collection = database.get_collection("Challenges")

class ChallengeOptions(discord.ui.View) :
    def __init__ (self):
        super().__init__()

    @discord.ui.button(label="Close Challenge", style=discord.ButtonStyle.danger)
    async def CloseThread(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.channel.delete()


def break_string_into_chunks(input_string, chunk_size=2000):
    chunks = []
    current_chunk = ''

    while input_string:
        # Check if the remaining string is less than the chunk size
        if len(input_string) <= chunk_size:
            chunks.append(input_string)
            break

        # Find the last newline character within the chunk size
        last_newline_index = input_string.rfind('\n\n', 0, chunk_size)

        if last_newline_index != -1:
            # Include the newline character and split the string
            current_chunk += input_string[:last_newline_index + 1]
            input_string = input_string[last_newline_index + 1:]
        else:
            # No newline found in the chunk, break at the specified size
            current_chunk += input_string[:chunk_size]
            input_string = input_string[chunk_size:]

        chunks.append(current_chunk)
        current_chunk = ''

    return chunks


client = commands.Bot(command_prefix="||||||", intents=discord.Intents.all())

@client.event
async def on_ready():
    commands = await client.tree.sync()
    print(f'{len(commands)} command(s) synced')

langs = ['javascript', 'java', 'c#', 'python', 'typescript', 'c++']
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
    
    filter = {"languages": {"$in": ["python"]}}
    if difficulty != "any":
        filter["difficulty"] = int(difficulty)

    threadType = ChannelType.private_thread if private else ChannelType.public_thread


    channel = client.get_channel(int("1172624718818459698"))
    thread = await channel.create_thread(
        name="Loading...",
        type=threadType
    )
    if not private:
        system_message = [message async for message in channel.history(limit=1)][0]
        if "started a thread" in system_message.system_content:
            await system_message.delete()

    await thread.add_user(interaction.user)


    embed=discord.Embed(title="Challenge Started", description=f"Loading...", color=0x1f5ad1)
    embed.set_footer(text="Please wait...")
    await interaction.response.send_message(embed=embed, ephemeral=private)

    docs = list(collection.find(filter))
    doc = docs[random.randint(0, len(docs) - 1)]

    
    embed=discord.Embed(title=doc["name"], description=doc["category"], color=0x1f5ad1)
    embed.add_field(name="Code Wars Link", value=doc["url"], inline=True)
    embed.add_field(name="Difficulty", value=doc["difficulty"], inline=True)
    embed.set_footer(text="Support Languages: " + " ".join(doc["languages"]))

    content = doc["description"]
    cleaned_content = re.sub(r'<[^<]+?>', '', content)
    cleaned_content= re.sub(r'\n{3,}', '\n\n', cleaned_content)
    cleaned_content.replace("~~~", "")

    result_chunks = break_string_into_chunks(cleaned_content)
    
    await thread.edit(name=doc["name"])
    await thread.send(embed=embed, view=ChallengeOptions())

    for index,chunk in enumerate(result_chunks):
        if (index == 0):
            await thread.send(chunk)
        else:
            await thread.send(chunk)

    embed=discord.Embed(title="Challenge Started", description=f"View the challenge here: {thread.jump_url}", color=0x1f5ad1)
    embed.add_field(name="Title", value=doc["name"])
    embed.add_field(name="Difficulty", value=doc["difficulty"])
    embed.set_footer(text="Support Languages: " + " ".join(doc["languages"]))
    await interaction.edit_original_response(embed=embed)


client.run(os.getenv('bot_token'))

