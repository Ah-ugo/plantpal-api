from fastapi import FastAPI
from Routers import auth

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])