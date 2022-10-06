from dataclasses import dataclass
from typing import Literal

MeetID = int
AthleteID = int
TeamID = str


@dataclass
class Athlete:
    id: AthleteID
    team: TeamID
    first_name: str
    last_name: str

@dataclass
class Meet:
    id: MeetID


@dataclass
class Result:
    athlete_id: AthleteID
    meet_id: MeetID
    time: float
    score: int
    place: int
    team_id: int
    year: Literal["FR", "SO", "JR", "SR"]
    last_name: str
    first_name: str
