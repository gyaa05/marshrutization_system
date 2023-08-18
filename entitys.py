from pydantic import BaseModel


class EntityTeam(BaseModel):
    name: str

class EntityStation(BaseModel):
    name: str
    description: str
    latitude: float
    longtitude: float
    flag: str

class Freeze(BaseModel):
    team_id: int
    station_id: int

class Unfreeze(BaseModel):
    team_id: int
    flag: str

class TeamId(BaseModel):
    team_id: int