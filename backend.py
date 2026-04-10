from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# TEMP STORAGE
storage = {}

@app.get("/")
def home():
    return {"message": "CrypTalk backend running"}

class Message(BaseModel):
    sender: str
    receiver: str
    encrypted: str
    key: str
    nonce: str
    sender_lang: str
    receiver_lang: str
    emotion: str
    tagged_text: str

@app.post("/send")
def send_message(msg: Message):
    global storage
    storage = msg.dict()
    return {"status": "stored"}

@app.get("/get")
def get_message():
    return storage
