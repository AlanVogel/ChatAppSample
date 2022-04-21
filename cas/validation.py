from pydantic import (
    BaseModel,
    validator,
    ValidationError,
)
from email_validator import (
    validate_email,
    EmailNotValidError,
)


class BaseName(BaseModel):
    nick_name: str


class Login(BaseModel):
    email: str
    password: str


class RegisterUserCheck(BaseName, Login):

    @validator("email")
    def is_email_valid(cls, email):
        try:
            return validate_email(email)
        except EmailNotValidError as e:
            raise ValueError(f"{email} is not a valid email: {e}")


class RoomCheck(BaseModel):
    user_id: int
    room_name: str


class MessageCheck(RoomCheck):
    msg: str


def validation_check(data: dict, checker):
    try:
        checker(**data)
    except ValidationError as e:
        return str(e)
