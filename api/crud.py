from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from api import models, schemas


def get_benefactor(db: Session, benefactor_id: int) -> schemas.Benefactor:
    """Queries the database for a benefactor with the given ID

    Args:
        db: Local database session
        benefactor_id: ID of desired benefactor

    Returns: Benefactor if found, else None
    """
    return db.query(models.Benefactor).filter(
        models.Benefactor.id == benefactor_id).first()


def add_benefactor(
        db: Session,
        benefactor: schemas.BenefactorIn) -> schemas.Benefactor:
    """Adds a benefactor with the provided information.

    Args:
        db: Local database session
        benefactor: Object that contains all benefactor attributes

    Returns: Benefactor with newly added info
    """
    benefactor_info = jsonable_encoder(benefactor)
    new_benefactor = models.Benefactor(**benefactor_info)
    db.add(new_benefactor)
    db.commit()
    db.refresh(new_benefactor)
    return new_benefactor


def update(db_session: Session, *, benefactor: schemas.Benefactor,
           benefactor_up: schemas.BenefactorIn) -> schemas.Benefactor:
    """Updates a benefactor object with provided information

    Args:
        db_session: Local database session
        benefactor: Original record
        benefactor_up: Contains information to update the original record

    Returns: Benefactor with updated information
    """
    user_data = jsonable_encoder(benefactor)
    update_data = benefactor_up.dict(skip_defaults=True)
    for field in user_data:
        if field in update_data:
            setattr(benefactor, field, update_data[field])

    db_session.add(benefactor)
    db_session.commit()
    db_session.refresh(benefactor)
    return benefactor
