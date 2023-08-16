from typing import Set, Literal

from pydantic import BaseModel, validator, conlist, conint, field_validator


class FilterData(BaseModel):
    difficulty: Set[Literal["easy", "medium", "hard"]] = {}
    rating: conlist(conint(ge = 0, le = 5), min_length = 2, max_length = 2) = [0, 5]
    timespan: Literal["day", "week", "month", "year", "alltime"] = 0
    
    @field_validator("rating")
    def fix_rating_order(cls, value):
        # If rating is out of order, fix it
        return sorted(value)
    
    @field_validator("timespan")
    def convert_timespan_value_to_days(cls, value):
        return {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365,
            "alltime": 0
        }[value]


class SearchData(BaseModel):
    filters: FilterData
    sorting: Literal["time", "rating"]
    search: str
