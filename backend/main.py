from fastapi import FastAPI
from auth import login_user
from database import get_db
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}

@app.post("/login")
def login(data: dict):
    return login_user(data)
