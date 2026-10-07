# WHAT — Starts the API and answers the health check.
# WHY — This is the file we run. The other folders plug in here.
# HOW — FastAPI serves GET /health. On startup it checks the Supabase connection. Running this file starts Uvicorn on port 4020.
# IMPORTANT — Patient rules do not belong here. They go in routes, controllers, and models. If .env is missing, startup stops on purpose.

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config.database import engine

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.info("Supabase database connection succeeded")
    except Exception:
        logger.exception("Supabase database connection failed")
        raise
    yield
    await engine.dispose()


app = FastAPI(title="FASTAPI_v1", lifespan=lifespan)

# The Vite app will call this API from these local addresses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=4020, reload=True)
