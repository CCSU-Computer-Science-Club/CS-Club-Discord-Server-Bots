from better_profanity import profanity
import pymongo
from CSBotCommon import PalmApi
import time
import datetime
import os
from dotenv import load_dotenv
load_dotenv()




class ProfanityDB:
    
    def __init__(self,document_data):
        self.document_data=document_data     
        # set up DB connection
        self.db_client = pymongo.MongoClient(os.getenv('mongo_string'))
        self.database = self.db_client.get_database("CodingChallengeBot")
        self.collection = self.database.get_collection("Users")
        

    def record_event_to_db(self ):
        # Check if user exist in DB if so update record else add record
        result = self.collection.find_one({"_id": self.document_data['_id']})
        if result:
            self.update_record()       
        else:
            insert_result = self.collection.insert_one(self.document_data)
            if insert_result.inserted_id:
                print("adding new record")
                return True
            else:
                return False
        
    def update_record(self):
        user_filter = {"_id":self.document_data['_id']}
        # Specify the new "profanity_warnings" entry
        new_offense =self.document_data['profanity_warnings'][0]    
        updated_document = {"$push": {"profanity_warnings": new_offense}}
        # Update the document with a new "profanity_warnings" entry
        result = self.collection.update_one(
            user_filter,
            updated_document
        )   
        if result.modified_count > 0:
            print("updating record")
            return True
        else:
            return False
        
class Hand_profanity:
    decision= False
    # Get the current time
    def __init__(self,discord_user_id,message_content):
        self.discord_user_id =discord_user_id
        self.severity_level= ""
        self.profanity_words =[]
        self.message_content =message_content
        
        current_time = datetime.datetime.utcnow()
        current_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.date = current_time
        
    def determine_severity_level(self):
        # Initialize Palm AI instance with API key from environment variable
        palm_ai = PalmApi("", os.getenv('palm_api_key'))
      
        palm_ai.prompt = f"""
        You are an AI function in my code that acts as a sentiment analysis tool.
        Your task is to analyze the provided text input string and determine its severity level based on a range of 0 to 5, where 5 represents extremely offensive content.
        You are going to be reading user messages from Discord. Make sure to analyze all profanity words used by the user in that message.
        If you are unable to determine the severity level, return None.
        Remember, you are a function that returns a value.
        Here is the text for you to process: {self.message_content}
        """
        self.severity_level = palm_ai.text_generator_agent()
        
        # Check if severity level is within the specified range (0-5)
        if self.severity_level is not None:
            unable_to_determine ="0"
            try:
                self.severity_level = int(self.severity_level)
                if self.severity_level  >= 1:
                    return self.severity_level
                else:
                    return unable_to_determine
            except ValueError:
                return unable_to_determine
        else:
            return 0
            
        
    def is_it_bad_word(self):
        self.descision = profanity.contains_profanity(self.message_content)
        if self.descision == True: 
            for word in self.message_content.split():
                if profanity.contains_profanity(word):
                    self.profanity_words.append(word)  
            descision_onj ={
                "severity_level": self.determine_severity_level(),
                "profanity_words":self.profanity_words
            }
            document_data ={
                "_id":self.discord_user_id,
                "profanity_warnings":[      
                    {
                    "message_content" :self.message_content,
                    "profanity_words":self.profanity_words,
                    "severity_level":descision_onj["severity_level"],
                    "date":self.date,
                    
                    },    
                ],
            }
            profanity_db_instace = ProfanityDB(document_data).record_event_to_db()
            
            return self.descision
        else:
            return False
            
        
    def warn_user(self, warning_message):
        # Check user DB check number of offenses based on some rules take action
        # create  private thread with warning message user. 
        pass
    
    def check_action_rule(self):
        # Check user DB check number of offenses based on some rules take action
        
        if 1:
            self.warn_user("Kicking you out because of ....")
        elif 2:
            self.warn_user("Kicking you out because of ....")
        elif 3:
            self.warn_user("Kicking you out because of ....")
           
        pass
    
    def add_to_probation(self):
        
        # warn user
        self.warn_user("Watchout ... buddy")

        pass
    
    def kick_user(self):
        # warn user
        self.warn_user("Kicking you out because of ....")
        pass
    
    
    # # test:






document={
    "_id": "gigi_gio",
    "profanity_warnings": [
        {
            "message_content": "Lorem ipsum dolor sit amet",
            "profanity_words": "Lorem",
            "severity_level":4,
            "date": "2023-09-09T10:45:00.123Z"
        },
        {
           "message_content" :"sdsc sdscsfcsd",
           "profanity_words":"#4343223",
           "severity_level":1,
           "date":"2023-09-09T05:21:02.896Z"
        },
        {
           "message_content" :"sdsc sdscsfcsd",
           "profanity_words":"#4343223",
           "severity_level":3,
           "date":"2023-09-09T05:21:02.896Z"
        },
    ]
}
document1 ={
    "_id":"65596dfc41ad54e01f806943",
    "profanity_warnings":[      
        {
           "message_content" :"sdsc sdscsfcsd",
           "profanity_words":"#4343223",
           "severity_level":4,
           "date":"2023-09-09T05:21:02.896Z"
        },
           
    ]    
}

# db = ProfanityDB(document1)
# print(db.record_event_to_db())

handle =Hand_profanity("ddsdsjjr5555", "That  did a very good H4ndjob.").is_it_bad_word()
print(handle)
