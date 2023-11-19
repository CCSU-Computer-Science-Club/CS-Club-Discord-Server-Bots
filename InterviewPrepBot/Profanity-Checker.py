from better_profanity import profanity
import pymongo
import os
from dotenv import load_dotenv
load_dotenv()




document={
    "_id": "65596dfc41ad54e01f806943",
    "profanity_warnings": [
        {
            "message_content": "Lorem ipsum dolor sit amet",
            "profanity_word": "Lorem",
            "date": "2023-09-09T10:45:00.123Z"
        }
    ]
}


document1 ={
    "_id":"65596dfc41ad54e01f806943",
    "profanity_warnings":[      
        {
           "message_content" :"sdsc sdscsfcsd",
           "profanity_word":"#4343223",
           "date":"2023-09-09T05:21:02.896Z"
        },
           
    ]    
}


class ProfanityDB:
    
    def __init__(self,document_data):
        
        
        # set up DB connection
        self.db_client = pymongo.MongoClient(os.getenv('mongo_string'))
        self.database = self.db_client.get_database("CodingChallengeBot")
        self.collection = self.database.get_collection("Users")
        self.document_data=document_data
        
    def record_event_to_db(self ):
        # if "profanity_warnings" not in self.collection.keys():
        #     self.collection["profanity_warnings"] = []
        
        # else:
        #     pass
        print("here")
        result = self.collection.insert_one(self.document_data)
       
    
        if result.inserted_id:
            print(result)
            return True
        else:
            print("nooo")
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
            return True
        else:
            return False
   
        


# test:
db = ProfanityDB(document1)
print(db.update_record())


class Hand_profanity:
    decision= False
    def __init__(self,discord_user_id,message_content):
        self.discord_user_id =discord_user_id
        self.severity_level= ""
        self.profanity_word =""
        self.message_content =message_content
        self.date = "" 
        

    
    def is_it_bad_word(self):
        self.descision = profanity.contains_profanity(self.message_content)
        return self.descision
        
    
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
    
    