from fastapi import FastAPI
from pydantic import BaseModel
import logging
import json
from datetime import datetime, timezone

app = FastAPI()

# Logger dédié qui écrit du JSON, une ligne par événement
logger = logging.getLogger("login_events")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()  # écrit sur stdout, Docker capture ça nativement
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

FAKE_USER = {"email": "test@test.com", "password": "1234"}

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    success = data.email == FAKE_USER["email"] and data.password == FAKE_USER["password"]

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "login_attempt",
        "email": data.email,
        "success": success,
    }
    logger.info(json.dumps(event))

    if success:
        return {"status": "ok"}
    else:
        return {"status": "erreur"}