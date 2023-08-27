from fastapi import APIRouter, HTTPException
from typing import List
from app.models.room import Room
from app.models.user import User
from app.models.chat_messege import Chat_Messege
from app.serializers.serializers import MessageOut, MessageCreate
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi import APIRouter
from fastapi import Depends, FastAPI
import aiocache
from aiocache import caches, Cache
from aiocache.serializers import JsonSerializer
import json
from fastapi import Query

cache = caches.get("default")

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

@router.get("/chat-history/{room_id}", summary="Chat History")
async def chat_history(room_id: int):
    """
    Get the chat history of a room.
    """
    messages = await Chat_Messege.filter(room_id=room_id).order_by('-timestamp').prefetch_related('user')
    return messages



@router.get("/cached-chat-history/{room_id}", summary="Chat History")
async def chat_history(
    room_id: int,
    page: int = Query(1, description="Page number", ge=1),
    items_per_page: int = Query(10, description="Number of items per page", ge=1)
):
    """
    Get the paginated chat history of a room.
    """
    cached_data = await cache.get(str(room_id))

    if cached_data:
        cached_messages = json.loads(cached_data)
    else:
        messages = await Chat_Messege.filter(room_id=room_id).order_by('-timestamp').prefetch_related('user')

        serialized_messages = [
            {
                "id": message.id,
                "text": message.text,
                "timestamp": message.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "user_id": message.user_id,
                "room_id": message.room_id
            }
            for message in messages
        ]

        await cache.set(str(room_id), json.dumps(serialized_messages), ttl=60)
        cached_messages = serialized_messages

    total_messages = len(cached_messages)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_messages = cached_messages[start_idx:end_idx]

    return {
        "total_messages": total_messages,
        "messages": paginated_messages
    }