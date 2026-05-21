from pydantic import BaseModel


class ScheduleRequest(BaseModel):
    teachers: dict
    courses: dict
    num_rooms: int
    cohorts: list
    days: list
    hours: list