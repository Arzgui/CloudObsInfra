from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

FAKE_USER = {"email": "test@test.com", "password": "1234"}

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    if data.email == FAKE_USER["email"] and data.password == FAKE_USER["password"]:
        return {"status": "ok"}
    else:
        return {"status": "erreur"}