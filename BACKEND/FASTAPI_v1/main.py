# WHAT — Starts the API and answers the health check.
# WHY — This is the file we run. The other folders plug in here.
# HOW — FastAPI serves GET /health. On startup it checks Supabase, creates the patients table, and seeds 20 fictional patients when that table is empty. Running this file starts Uvicorn on port 4020.
# IMPORTANT — Patient rules do not belong here. They go in routes, controllers, and models. If .env is missing, startup stops on purpose.

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config.database import DatabaseBase, engine
from models.patient import seed_patients_if_empty
from routes.notes import note_router
from routes.patients import patient_router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))
            await connection.run_sync(DatabaseBase.metadata.create_all)
        logger.info("Supabase database connection succeeded")
        inserted_count = await seed_patients_if_empty()
        if inserted_count:
            logger.info("Seeded %s fictional patients", inserted_count)
        else:
            logger.info("Patient seed skipped because rows already exist")
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


app.include_router(patient_router)
app.include_router(note_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=4020, reload=True)
