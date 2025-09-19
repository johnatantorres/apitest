from pydantic import BaseModel, Field

class Message(BaseModel):
    query: str

class FixtureInput(BaseModel):
    team_1: str = Field(description="first team to search")
    team_2: str = Field(description="second team to search")

class FixtureInputTeam(BaseModel):
    team: str = Field(description="team to search")

class FixtureInputDate(BaseModel):
    date: str = Field(description="date to search in format YYYY-MM-DD")

class FixtureInputDates(BaseModel):
    date_1: str = Field(description="first date to search in format YYYY-MM-DD")
    date_2: str = Field(description="second date to search in format YYYY-MM-DD")

class Preferences:
    favorite_sport: str = None
    sport_id: int = None
