'''
TASK4: Abdullah Salih.
1- run "pip install -r requirements.txt"
2- run the main.py file in root dir.
3- sockets.py is for running socket servers for each chat room
4. models are inside the app>models module.
5. cleint.py and client2.py and seperate python scripts, first one connects to chatroom 1 as user 1 second one connects to chatroom 2 as user 2
6. make sure to populate the database if empty for testing.
7. run the client by : "python client.py" 

'''

from fastapi import HTTPException
from fastapi import FastAPI
from app.dependencies.database import Tortoise, init_tortoise, close_tortoise
from app.routes import user_routes, chat_routes
from fastapi.middleware.cors import CORSMiddleware
from app.models.chat_messege import Chat_Messege
from app.serializers.serializers import MessageOut, MessageCreate
import socketio
from app.models.room import Room
from app.models.user import User
from app.models.chat_messege import Chat_Messege
from sockets import sio_app
from sockets import send_message_to_channel

app = FastAPI()

app.include_router(user_routes.router, prefix="/users", tags=["users"])
app.include_router(chat_routes.router, prefix="/chat", tags=["chat"])

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_db():
    await init_tortoise(app)

@app.on_event("shutdown")
async def shutdown_db():
    await close_tortoise(app)

@app.post("/send-message", response_model=MessageOut)
async def send_message(message_data: MessageCreate):
    room_id = message_data.room_id
    user_id = message_data.user_id
    
    room_sid = f'{room_id}_{user_id}'
    
    try:
        room = await Room.get(id=room_id)
    except Room.DoesNotExist:
        raise HTTPException(status_code=404, detail="Room not found")

    try:
        user = await User.get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    
    message = await Chat_Messege.create(text=message_data.text, user=user, room=room)
    
    message_out = MessageOut(
        id=message.id,
        text=message.text,
        timestamp=message.timestamp,
        user_id=message.user_id,
        room_id=message.room_id
    )
    
    await send_message_to_channel(user_id, message_data.text, room_sid)

    return message_out

app.mount('/', app=sio_app)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
