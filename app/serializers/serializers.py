from pydantic import BaseModel
from datetime import datetime

class RoomCreate(BaseModel):
    name: str

class RoomInDB(RoomCreate):
    id: int

class RoomOut(RoomInDB):
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    text: str
    # user_id: int
    room_id: int

class MessageInDB(MessageCreate):
    id: int
    timestamp: datetime

class MessageOut(BaseModel):
    id: int
    text: str
    timestamp: datetime
    user_id: int
    room_id: int