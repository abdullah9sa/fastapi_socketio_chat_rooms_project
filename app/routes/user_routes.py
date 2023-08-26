from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User, UserInCreate, user_pydantic_out, UserOutResponse
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
import datetime
import bcrypt
import jwt

router = APIRouter()


# Your JWT secret key (should be kept secret)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# OAuth2 password bearer for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Verify user credentials and generate JWT token
def authenticate_user(username: str, password: str):
    user = User.get(username=username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return user

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
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


