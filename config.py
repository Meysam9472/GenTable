from fastapi import FastAPI
from apps.time_table_maker import time_table
from apps.users import users


app = FastAPI()

app.include_router(time_table.router, tags=["time_table"])
app.include_router(users.router, tags=["users"])
