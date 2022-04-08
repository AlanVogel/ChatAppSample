from pydantic import (
    BaseModel,
    validator,
)
from email_validator import (
    validate_email,
    EmailNotValidError,
)


class Login(BaseModel):
    email: str
    password: str


class RegisterUserCheck(Login):
    nick_name: str

    @validator("email")
    def is_email_valid(cls, email):
        try:
            return validate_email(email)
        except EmailNotValidError as e:
            raise ValueError(f"{email} is not a valid email: {e}")


class MessageCheck(RegisterUserCheck):
    sender_id: int
    message: str


class ConversationCheck(RegisterUserCheck):
    conversation_name: str
