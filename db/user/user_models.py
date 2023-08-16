from pydantic import BaseModel, validator, Field, field_validator


class UpdateUser(BaseModel):
    user_id: int = Field(alias = "userId")
    user_name: str = Field(alias = "userName")
    user_avatar: str = Field(alias = "userAvatar")
    
    @field_validator("user_id")
    def check_uid(cls, value):
        if value < 0:
            raise ValueError("The uid must be positive")
    
    @field_validator("user_name")
    def check_user_name(cls, value):
        if value == "":
            raise ValueError("The username must be positive")
