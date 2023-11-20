import discord
from discord.ext import commands
import pymongo
import pprint
import google.generativeai as palm
import google.auth.transport.requests
from google.protobuf import json_format
import dotenv
import os
from discord import ChannelType

class Bot:
    def __init__(self, botToken, mongoUri=None):
        if (mongoUri != None):
            self.mongoClient = pymongo.MongoClient(mongoUri)
        self.botClient = commands.Bot(command_prefix="||||||", intents=discord.Intents.all())
        self.botToken = botToken

    def run(self):
        self.botClient.run(self.botToken)

    def break_string_into_chunks(self, input_string, chunk_size=2000):
        chunks = []
        current_chunk = ''

        while input_string:
            if len(input_string) <= chunk_size:
                chunks.append(input_string)
                break

            last_newline_index = input_string.rfind('\n\n', 0, chunk_size)

            if last_newline_index != -1:
                current_chunk += input_string[:last_newline_index + 1]
                input_string = input_string[last_newline_index + 1:]
            else:
                current_chunk += input_string[:chunk_size]
                input_string = input_string[chunk_size:]

            chunks.append(current_chunk)
            current_chunk = ''
        return chunks

    def create_private_thread(self,user_id,channel_id,message_object):
        async def on_ready():
            print("Bot reading, creating thread...")
            user = self.botClient.get_user(int(user_id))
            print(user)
            if user is None:
                return

            threadType = ChannelType.private_thread
            channel = self.botClient.get_channel(int(channel_id))
            print(channel.name)
            thread = await channel.create_thread(
                name=message_object['warning_type'],
                type=threadType
            )
            await thread.send(message_object['warning_message'])

            await thread.add_user(user)

            # Remove the event listener after creating the thread
            self.botClient.remove_listener(on_ready, 'on_ready')

    # Add the event listener
        self.botClient.add_listener(on_ready, 'on_ready')
               
class PalmApi:
    def __init__(self, prompt,palmp_api_key,output_max_length=None ):
        if (output_max_length!=None):
            self.output_max_length = output_max_length
        self.key = palmp_api_key
        self.refine_count = 0
        self.try_count = 0
        self.prompt = prompt
        self.response = ""
        self.output_max_length = output_max_length
        self.model = ""
        self.palm =""
        self.configue_client()

    def configue_client(self):

        try:
            self.palm = palm.configure(api_key=self.key)
            models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
            self.model = models[0].name
            #print(self.model)
        except:
            print("An error has occurred while trying to configue Palm AI client")

    def message_length_refiner_agent(self, ):
        """
        This method is intended to refine the previous AI output.
        It should make a request to get the previous output text to be re-adjusted depending on your preferences.
        Args:
            output_max_length (int): The maximum words output of the previous AI output. Assumin that each word has on average 6.5 characters.
        """

        original_prompt = self.prompt
        previous_ai_response = self.response
        refine_character_prompt = f"""
                                Here is my question {original_prompt}.
                                Here is your response {previous_ai_response}. You exceeded the word count of {self.output_max_length}. Make it shorter.
                                Rewrite your response to be {self.output_max_length} words!     
                                    """
        refined_output = self.text_generator_agent(refine_character_prompt)

        #print(f"Refine count: {self.refine_count}")
        return refined_output
    def text_generator_agent(self):
        completion = palm.generate_text(
            model=self.model,
            prompt=self.prompt,
            temperature=0,
            # The maximum length of the response
            max_output_tokens=800, )
        self.response = completion.result

        # Enter Character refiner function if the user provide max length and if AI agent exceed it.
        if self.output_max_length != None:
            if (len(self.response)) / 6.5 > self.output_max_length:
                self.message_length_refiner_agent(self.output_max_length)
        else:
            #print(f"Refine count: {self.refine_count} \nNumber of tries: {self.try_count}")
            return self.response

