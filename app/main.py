from dotenv import load_dotenv

load_dotenv()

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import GoogleAuthMiddleware, get_client_id

get_client_id()  # Fail fast before anything else is wired up, rather than per request.

from api.endpoints import router

# Origins allowed to call the API from a browser (the frontend), comma separated.
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(",") if origin.strip()]

app = FastAPI(title="Personal Wallet API")
# Added first, so it runs inside CORSMiddleware: preflight requests are answered by CORS
# and 401 responses still carry the CORS headers the browser needs to read them.
app.add_middleware(GoogleAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
