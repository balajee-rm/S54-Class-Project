from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import jwt
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = AsyncIOMotorClient(MONGO_URI)
user_collection = client.mydb.users

class User(BaseModel):
    username: str
    password: str

def create_access_token(data: dict):
    return jwt.encode({**data, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/singup")
async def signup(user: User):
    if await user_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail={"message": "User Already Exist"})
    hashed_password = pwd_context.hash(user.password)
    await user_collection.insert_one({"username": user.username, "password": hashed_password})
    return JSONResponse(status_code=200, content={"message": "User Registered"})

@app.post("/singin")
async def signin(user: User):
    db_user = await user_collection.find_one({"username": user.username})
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail={"message": "Invalid User"})
    token = create_access_token({"username": user.username}) 
    return JSONResponse(status_code=200, content={"access_token": token})

@app.get("/protected")
async def protected_route(username: str = Depends(get_current_user)):
    return JSONResponse(status_code=200, content={"message": f"Hi {username}, welcome"})


