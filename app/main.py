# app/main.py
from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from app.chat.services import initiate_chat_service, initiate_thread_service, get_users_service


from .database import get_db

app = FastAPI(
    title="ChatBet API",
    description="API for managing bets and chat interactions",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "CHATBET API IS RUNNING"}

@app.post("/initiate_thread/{user_id}")
async def initiate_thread(user_id, db=Depends(get_db)):
    return initiate_thread_service(user_id, db)

@app.get("/get_users/")
async def get_users(db=Depends(get_db)):
    return get_users_service(db)

@app.get("/initiate_chat/{thread_id}")
async def initiate_chat(thread_id, db=Depends(get_db)):
    return initiate_chat_service(thread_id, db)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)