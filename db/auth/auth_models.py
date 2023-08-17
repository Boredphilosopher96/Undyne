from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, Field, EmailStr, HttpUrl, field_validator


class UserModel(BaseModel):
    user_id: str = Field(alias = "sub")
    user_name: str = Field("", alias = "nickname")
    user_email: EmailStr = Field(alias = "email")
    user_avatar: Optional[HttpUrl] = Field(alias = "picture")
    creation_date: Optional[datetime] = Field(None, exclude = True)
    
    @field_validator("user_avatar")
    def convert_url_to_string(cls, value):
        if value is not None:
            return str(value)
