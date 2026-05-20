from fastapi import FastAPI
from apps.time_table_maker import time_table
from apps.users import manage_users


app = FastAPI()

app.include_router(time_table.router, tags=["time_table"])
app.include_router(manage_users.router, tags=["users"])
