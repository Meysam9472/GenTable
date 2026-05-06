from fastapi import FastAPI
from routers import time_table, users

app = FastAPI()

app.include_router(time_table.router, tags=["time_table"])
app.include_router(users.router, tags=["users"])
