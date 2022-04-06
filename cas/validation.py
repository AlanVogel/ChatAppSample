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
    key_word: str

    @validator("nick_name")
    def is_valid_name(cls, nick_name):
        for letter in nick_name:
            if not letter.isalpha():
                raise ValueError(f"{nick_name} is not a valid name!")
        return nick_name

    @validator("email")
    def is_email_valid(cls, email):
        try:
            valid = validate_email(email)
            if valid:
                return valid.email
        except EmailNotValidError as e:
            raise ValueError(f"{email} is not a valid email: {e}")


class Chat(RegisterUser):
    message: str
