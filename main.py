
from fastapi import FastAPI
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

app = FastAPI()

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
