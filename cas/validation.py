from pydantic import (
    BaseModel,
    validator,
)
from email_validator import (
    validate_email,
    EmailNotValidError,
)


class RegisterUser(BaseModel):
    nick_name: str
    email: str

    @validator("email")
    def is_email_valid(cls, email):
        try:
            return validate_email(email)
        except EmailNotValidError as e:
            raise ValueError(f"{email} is not a valid email: {e}")


class Message(RegisterUser):
    sender_id: int
    message: str


class Conversation(RegisterUser):
    conversation_name: str
