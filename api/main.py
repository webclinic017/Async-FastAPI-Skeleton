import os
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from api import crud, schemas, models, database

models.Base.metadata.create_all(bind=database.engine)

REDIS_HOST = os.environ.get("REDIS_HOST", None)
REDIS_PORT = os.environ.get("REDIS_PORT", None)
REDIS_SETTINGS = RedisSettings(REDIS_HOST, REDIS_PORT)

app = FastAPI()


def get_db():
    try:
        db = database.SessionLocal()
        yield db
    finally:
        db.close()


async def enqueue_email(id: int):
    # background task adds to the queue
    WORKER_POOL = await create_pool(REDIS_SETTINGS)
    await WORKER_POOL.enqueue_job("send_emails", id)


@app.get("/object/{id}", response_model=schemas.Benefactor)
async def get_object_info(id: int, db: Session = Depends(get_db)):
    # check if benefactor exists, return 404 error otherwise
    result = crud.get_benefactor(db, benefactor_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benefactor not found")
    return result


@app.post("/object/{id}", response_model=schemas.Benefactor)
async def update_object(id: int, background_tasks: BackgroundTasks, benefactor: schemas.BenefactorIn,
                        db: Session = Depends(get_db)):
    # check if benefactor exists
    result = crud.get_benefactor(db, benefactor_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Benefactor not found")

    crud.update(db, benefactor=result, benefactor_up=benefactor)
    background_tasks.add_task(enqueue_email, id)

    # return latest benefactor
    latest_benefactor = crud.get_benefactor(db, benefactor_id=id)
    return latest_benefactor
