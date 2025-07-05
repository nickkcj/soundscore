from pydantic import BaseModel, field_validator, model_validator
from typing import Any

class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

    @field_validator('username')
    @classmethod
    def username_validation(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 20:
            raise ValueError('Username must be no more than 20 characters long')
        return v

    @field_validator('email')
    @classmethod
    def email_validation(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @field_validator('password')
    @classmethod
    def password_validation(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @model_validator(mode='after')
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
