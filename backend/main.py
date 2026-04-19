from fastapi import FastAPI
from backend.auth import login_user  # adjust if needed

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}

@app.post("/login")
def login(data: dict):
    return login_user(data)
