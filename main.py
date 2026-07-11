from dotenv import load_dotenv

load_dotenv()

import uvicorn
from fastapi import FastAPI

from api.endpoints import router

app = FastAPI(title="Personal Wallet API")
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
