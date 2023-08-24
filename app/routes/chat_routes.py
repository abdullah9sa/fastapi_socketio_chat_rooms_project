from fastapi import APIRouter, HTTPException
from typing import List
from app.models.room import Room
from app.models.user import User
from app.models.chat_messege import Chat_Messege
from app.serializers.serializers import MessageOut, MessageCreate
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi import APIRouter

router = APIRouter()

Room_Pydantic = pydantic_model_creator(Room, name="Room")
Message_Pydantic = pydantic_model_creator(Chat_Messege, name="Message")

# Create a room
@router.post("/create-room", response_model=Room_Pydantic, summary="Create a Room")
async def create_room(name: str):
    """
    Create a new chat room.
    """
    room = await Room.create(name=name)
    return room

# Join a user to a room
@router.post("/join-room/{room_id}/{user_id}", summary="Join a Room")
async def join_room(room_id: int, user_id: int):
    """
    Join a user to a chat room.
    """
    room = await Room.get(id=room_id)
    user = await User.get(id=user_id)
    await room.users.add(user)
    return {"message": "User joined the room"}

# Route to return chat history
@router.get("/chat-history/{room_id}", response_model=List[MessageOut], summary="Chat History")
async def chat_history(room_id: int):
    """
    Get the chat history of a room.
    """
    room = await Room.get(id=room_id)

    messages = await Chat_Messege.filter(room_id=room_id).order_by('-timestamp').prefetch_related('user')
    return messages
