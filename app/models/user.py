from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
import datetime

class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=200, null=False, unique=True)
    password = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.datetime.utcnow)

# Pydantic models for input and output
UserInCreate = pydantic_model_creator(User, name="UserInCreate", exclude_readonly=True)

user_pydantic_out = pydantic_model_creator(User,name="UserOut",exclude=("password",))

# Custom Pydantic models for output
class UserOutResponse(BaseModel):
    id: int
    username: str
    email: str
    join_date: datetime.datetime

