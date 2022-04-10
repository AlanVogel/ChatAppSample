from pydantic import (
    BaseModel,
    validator,
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


class RoomCheck(BaseName):
    room_name: str


class RoomJoinLeave(RoomCheck):
    button: str

    @validator("button")
    def button_string(cls, button):
        if button != 'join' and button != 'leave':
            raise ValueError(f"{button} is not valid! Try use join/leave")
        return button


class MessageCheck(RoomCheck):
    msg: str
