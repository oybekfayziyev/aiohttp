import datetime
from typing import Optional
from app.models import User
from pydantic import BaseModel, validator


class TokenObtainSerializer(BaseModel):
    username: str
    password: str


class UserCreateSerializer(BaseModel):
    username: str
    name: str
    surname: Optional[str]
    password: str
    password2: str

    @validator("password2")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        if len(values["password"]) <= 7:
            raise ValueError("Password length must be greater than 8")
        return v

    async def save(csl, data):

        hashed_password = User.make_password(data["password"])
        data.pop("password2")
        data["password"] = hashed_password
        user = await User.create_user(data)
        return user


class EventCreateSerializer(BaseModel):

    title: str
    description: Optional[str]
    price: float
    remain: int
    date: datetime.date


class CouponSerializer(BaseModel):
    user: int
    event: int
