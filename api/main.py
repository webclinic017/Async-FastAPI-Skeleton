import os

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from api import crud, schemas, models, database

models.Base.metadata.create_all(bind=database.engine)

REDIS_HOST = os.environ.get("REDIS_HOST", None)
REDIS_PORT = os.environ.get("REDIS_PORT", None)
REDIS_SETTINGS = RedisSettings(REDIS_HOST, REDIS_PORT)

app = FastAPI()


async def get_worker_pool():
    """Provides worker pool connection asynchronously."""
    try:
        pool = await create_pool(REDIS_SETTINGS)
        yield pool
    finally:
        pool.close()


async def get_db():
    """Provides DB connection."""
    try:
        db = database.SessionLocal()
        yield db
    finally:
        db.close()


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
async def update_object(id: int, benefactor: schemas.BenefactorIn,
                        db: Session = Depends(get_db), pool=Depends(get_worker_pool)):
    """Check if benefactor exists, and if so, make changes to the record.

    Args:
        id: ID of benefactor
        background_tasks: BackgroundTasks object automatically created by FastAPI
        benefactor: Updated information for benefactor with given ID
        db: Local DB session from generator

    Returns: Newly updated benefactor info in JSON form
    """
    result = crud.get_benefactor(db, benefactor_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benefactor not found")

    result = crud.update(db, benefactor=result, benefactor_up=benefactor)
    await pool.enqueue_job("send_emails", id)

    return result
