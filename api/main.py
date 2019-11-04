import os
from typing import List

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from api import crud, schemas, models, database

models.Base.metadata.create_all(bind=database.engine)

REDIS_HOST = os.environ.get("REDIS_HOST", None)
REDIS_PORT = os.environ.get("REDIS_PORT", None)
REDIS_SETTINGS = RedisSettings(REDIS_HOST, REDIS_PORT)
SUBSCRIBERS = ["sub1@emailserver.com", "sub2@emailserver.com"]

app = FastAPI()
conn = {}


async def get_worker_pool():
    """Provides worker pool connection asynchronously."""
    try:
        pool = await create_pool(REDIS_SETTINGS)
        yield pool
    finally:
        pool.close()


def get_db():
    """Provides DB connection."""
    try:
        db = database.SessionLocal()
        yield db
    finally:
        db.close()


async def enqueue_email(id: int, subscribers: List[str]):
    """Enqueues emailing task"""
    await conn["pool"].enqueue_job("send_emails", id, subscribers)


@app.on_event("startup")
async def startup():
    conn["pool"] = await create_pool(REDIS_SETTINGS)


@app.on_event("shutdown")
async def shutdown():
    conn["pool"].close()


@app.get("/object/{id}", response_model=schemas.Benefactor)
async def get_object_info(id: int, db: Session = Depends(get_db)):
    """Check if benefactor exists, return 404 error otherwise.

    Args:
        id: ID of benefactor
        db: Local DB session from generator

    Returns: Benefactor info in JSON form
    """
    result = crud.get_benefactor(db, benefactor_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benefactor not found")
    return result


@app.post("/object/{id}", response_model=schemas.Benefactor)
async def update_object(id: int, benefactor: schemas.BenefactorIn, background_task: BackgroundTasks,
                        db: Session = Depends(get_db)):
    """Check if benefactor exists, and if so, make changes to the record.

    Args:
        id: ID of benefactor
        benefactor: Updated information for benefactor with given ID
        db: DB session from generator

    Returns: Newly updated benefactor info in JSON form
    """
    result = crud.get_benefactor(db, benefactor_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benefactor not found")

    result = crud.update(db, benefactor=result, benefactor_up=benefactor)
    background_task.add_task(enqueue_email, id, SUBSCRIBERS)

    return result
