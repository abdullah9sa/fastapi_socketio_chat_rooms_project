from fastapi import APIRouter, HTTPException
from app.models.user import *
import bcrypt

router = APIRouter()
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
