import google.generativeai as palm
import os
import dotenv
import os


dotenv.load_dotenv()
palm_api_key = os.getenv("palm_api_key")


global refine_count
global try_count
refine_count = 0
try_count=0

def hey_bot(prompt):
    global refine_count  
    global try_count

    
    palm.configure(api_key=palm_api_key)
    
    completion = palm.generate_text(
        model="models/text-bison-001",
        prompt=prompt,
        temperature=0,
        max_output_tokens=800,
    )
    response = completion.result
    
    if len(response) > 2000:
        refine_count += 1
        refine_character_prompt = f"""Here is my question {prompt}.
         Here is your response {response}. You exceed the character count of 2000. Make it shorter."""
        hey_bot(refine_character_prompt)
        
    elif response == None:
        try_count+=1
        hey_bot(prompt)
        
    else:
        print(f"Refine count: {refine_count} \nNumber of tries: {try_count}")
        return response





