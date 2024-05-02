import os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_cors import CORS
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

class User(BaseModel):
    _userId: str = Field(default_factory=uuid.uuid4(), hidden=True)
    firstName: str
    lastName: str
    emailAddress: str

class Message(BaseModel):
    _messageId: str = Field(default_factory=uuid.uuid4(), hidden=True)
    _timestamp: str = Field(default_factory=lambda: datetime.now.strftime("%d/%m/%Y, %H:%M:%S"), hidden=True)
    senderUserId: str
    receiverUserId: str
    message: str

class SummaryText(BaseModel):
   text: str

load_dotenv()

app = FastAPI()
CORS(app)

openAIAPIKey = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openAIAPIKey)

@app.get("/bots/list")
async def list_bots():
    
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {openAIAPIKey}",
      "OpenAI-Beta": "assistants=v2",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.openai.com/v1/assistants", headers=headers)
        data = response.json()
        print(data)
        return(data)
    
@app.get("/bots/delete/{assistant_id}")
async def delete_bots(assistant_id: str):
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {openAIAPIKey}",
      "OpenAI-Beta": "assistants=v2",
    }
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"https://api.openai.com/v1/assistants/{assistant_id}", headers=headers)
        data = response.json()
        print(data)
        return(data)

@app.get("/threads/list")
async def list_bots():
    
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {openAIAPIKey}",
      "OpenAI-Beta": "assistants=v2",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.openai.com/v1/threads", headers=headers)
        data = response.json()
        print(data)
        return(data)
    
@app.post("/summary/")
async def add_summary(summaryText: SummaryText):
    assistant = client.beta.assistants.create(
  name="Summary Sage",
  instructions="""You are a professional AI summarization assistant.
  When a user provides text input, use the following step-by-step instructions to respond to user inputs. 
  Step 1 - The user will provide you with text.
  Step 2 - Analyze the text carefully by reading and understanding all of it.
  Step 3 - Identify the key points by extracting the most important information and key points from the text.
  Step 4 - Summarize the text while prioritizing conciseness while maintaining clarity, use the shortest possible phrases to represent each key point. Focus on factual points and avoid including unnecessary opinions or details.
  Step 5 - Present the summary by organizing it into a bulleted list.
  Step 6 - Uphold contextual accuracy, ensuring the summary accurately reflects the context of the original text, even with the brevity""",
  tools=[],
  model="gpt-4-turbo",
)
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=summaryText.text
)
    run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="""You are a professional AI summarization assistant.
  When a user provides text input, use the following step-by-step instructions to respond to user inputs. 
  Step 1 - The user will provide you with text.
  Step 2 - Analyze the text carefully by reading and understanding all of it.
  Step 3 - Identify the key points by extracting the most important information and key points from the text.
  Step 4 - Summarize the text while prioritizing conciseness while maintaining clarity, use the shortest possible phrases to represent each key point. Focus on factual points and avoid including unnecessary opinions or details.
  Step 5 - Present the summary by organizing it into a bulleted list.
  Step 6 - Uphold contextual accuracy, ensuring the summary accurately reflects the context of the original text, even with the brevity"""
)
    
    if run.status == 'completed': 
        responseMessages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        return responseMessages.data
    else:   
        return run.status

@app.get("/testopenaiapi")
async def test_openai_api():
    completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)
    return(completion.choices[0].message)


# USERS MOCK DATABASE
# FOR DEMO PURPOSES userId USES AN EXPECTED INCREMENTAL VALUE, OTHERWISE USE UUID
Users = [{
    "userId": "ABC001",
    "firstName": "John",
    "lastname": "Doe",
    "emailAddress": "john.doe@gmail.com"
},
    {
        "userId": "ABC002",
        "firstName": "Steve",
        "lastName": "Rogers",
        "emailAddress": "steverogers@gmail.com"
    }
]

# MESSAGES MOCK DATABASE
# FOR DEMO PURPOSES DATABASE STRUCTURE IS IN ITS SIMPLEST FORM, OTHERWISE OPTIMIZE WITH BETTER STRUCTURE TO REDUCE READ LOADS
Messages = [
    {
        "messageId": uuid.uuid4(),
        "senderUserId": "ABC001",
        "receiverUserId": "ABC002",
        "timestamp": "213123123",
        "message": "Hello"
    },
    {
        "messageId": uuid.uuid4(),
        "senderUserId": "ABC002",
        "receiverUserId": "ABC001",
        "timestamp": "213123123",
        "message": "Hello"
    }
]

# HELPER FUNCTION TO GENERATE EXPECTED INCREMENTAL USERID
def generate_user_id():
    lastUserId = Users[-1]["userId"]
    newUserId = f"ABC{int(lastUserId[3:]) + 1:03}"
    return newUserId

# RETURN ALL USERS IN MOCK DATABASE
@app.get("/users")
async def get_all_users():
    return Users

# RETURN USER IN MOCK DATABASE WITH USERID user_id
@app.get("/users/{user_id}")
async def get_user_by_id(user_id: str):
    # IF USER IS FOUND INSIDE THE MOCK DATABASE
    for user in Users:
        if user["userId"] == user_id:
            return user
    # IF USER IS NOT FOUND INSIDE MOCK DATABASE
    return "User Not Found"

# RETURN  ALL MESSAGES IN MOCK DATABASE
@app.get("/messages")
async def get_all_messages():
    return Messages

# RETURN MESSAGE IN MOCK DATABASE WITH SENDERUSERID AND RECEIVERUSERID user_id
@app.get("/messages/{user_id}")
async def get_messages_by_user(user_id: str):
    filteredMessages = []
    # IF MESSAGE IS FOUND INSIDE THE MOCK DATABASE
    for message in Messages:
        if message["senderUserId"] == user_id or message["receiverUserId"] == user_id:
            filteredMessages.append(message)
    
    # IF NO MESSAGE IS FOUND INSIDE THE MOCK DATABASE
    if (len(filteredMessages) == 0): return "Message Not Found"
    else: return filteredMessages

# ADD NEW USER
@app.put("/users")
async def add_user(user: User):
    # THIS DEMO DOES NOT ACCOUNT FOR MULTIPLE USERS WITH THE SAME FIRSTNAME, LASTNAME, AND/OR EMAILADDRESS
    newUser = {
        "userId": generate_user_id(),
        "firstName": user.firstName,
        "lastName": user.lastName,
        "emailAddress": user.emailAddress
    }

    Users.append(newUser)
    return newUser

# ADD NEW MESSAGE
@app.put("/messages")
async def add_message(message: Message):
    # CHECK IF SENDER AND RECEIVER IS THE SAME USER
    if (message.senderUserId != message.receiverUserId):
        newMessage = {
            "messageId": uuid.uuid4(),
            "timestamp": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            "senderUserId": message.senderUserId,
            "receiverUserId": message.receiverUserId,
            "message": message.message
        }
        
        Messages.append(newMessage)
        return newMessage
    else: return "Message Not Valid"
