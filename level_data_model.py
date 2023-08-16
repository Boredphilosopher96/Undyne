from typing import Literal

from pydantic import BaseModel, Field, conint, constr, conlist


class Arrow(BaseModel):
    """
    Represents an arrow in the level data.
    """
    
    direction: Literal["U", "D", "L", "R", "?"]
    reversed: bool
    delay: conint(ge = 0, le = 9999)
    speed: conint(ge = 1, le = 999)


class Attack(BaseModel):
    """
    Represents an attack in the level data.
    """
    
    attack_delay: conint(ge = 0, le = 9999) = Field(alias = "attackDelay")
    clockwise_shift: bool = Field(alias = "clockwiseShift")
    arrows: conlist(Arrow, min_length = 1, max_length = 50)


class LevelData(BaseModel):
    """
    Represents the overall level data.
    """
    
    attacks: conlist(Attack, min_length = 1, max_length = 40)
    title: constr(min_length = 3, max_length = 20)
    description: constr(min_length = 3, max_length = 200)
    difficulty: Literal["easy", "medium", "hard"]
    is_public: bool = Field(alias = "isPublic")
