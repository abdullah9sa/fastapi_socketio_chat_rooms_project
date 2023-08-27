from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import *
import datetime
import bcrypt
import jwt
from fastapi import HTTPException
from app.models.chat_messege import Chat_Messege
from app.serializers.serializers import MessageOut, MessageCreate
import socketio
from app.models.room import Room
from app.models.user import User
from app.models.chat_messege import Chat_Messege
from sockets import send_message_to_channel
import jwt
from fastapi import Header


router = APIRouter()


SECRET_KEY = "12345678"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

# OAuth2 password bearer for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def authenticate_user(username: str, password: str):
    user = await User.get_or_none(username=username)  # Use get_or_none to get a single user
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            print(f"Password hash of user {username}: {user.password}")
            return user


def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/{user_id}", response_model=user_pydantic_out, summary="Get User by ID", description="Retrieve user details by providing their ID.")
async def get_user(user_id: int):
    """
    Get User by ID
    Retrieve user details by providing their ID.
    
    :param user_id: ID of the user to retrieve.
    :return: User details.
    """
    user = await User.get_or_none(id=user_id)
    
    if user is None:
        error_msg = f"User with ID {user_id} not found"
        error_detail = {"error": error_msg}
        raise HTTPException(status_code=404, detail=error_detail)
    
    user_out_response = UserOutResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        join_date=user.join_date
    )
    return user_out_response

@router.post("/register", response_model=UserOutResponse, summary="Register User", description="Register a new user.")
async def register_user(user_data: UserInCreate):
    """
    Register User
    Register a new user.
    
    :param user_data: User data including username, email, and password.
    :return: Registered user details.
    """
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())

    # Create a new user using the data from the request
    new_user = await User.create(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password.decode('utf-8'),  # Store the hashed password in the database
    )

    user_out_response = UserOutResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        join_date=new_user.join_date
    )
    return user_out_response

def authenticate_token(authorization: str = Header(default=None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    # Assuming the token is in the format "Bearer <token>"
    try:
        _, token = authorization.split()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    return token

async def get_current_user(token: str = Depends(authenticate_token)):
    try:
        payload = jwt.decode(token, "12345678", algorithms=["HS256"])
        user_id = payload.get("sub")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT token expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")
    user = await User.get_or_none(username=user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
@router.post("/send-message", response_model=MessageOut)
async def send_message(message_data: MessageCreate, current_user: User = Depends(get_current_user)):
    room_id = message_data.room_id
    user_id = current_user.id  # Use the authenticated user's ID
    
    room_sid = f'{room_id}_{user_id}'
    
    try:
        room = await Room.filter(id=room_id).prefetch_related('users').first()
    except Room.DoesNotExist:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if current_user not in room.users:
        raise HTTPException(status_code=403, detail="User is not in the room")
    
    message = await Chat_Messege.create(text=message_data.text, user=current_user, room=room)
    
    message_out = MessageOut(
        id=message.id,
        text=message.text,
        timestamp=message.timestamp,
        user_id=message.user_id,
        room_id=message.room_id
    )
    
    await send_message_to_channel(user_id, message_data.text, room_sid)

    return message_out
