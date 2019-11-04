from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class Benefactor(Base):
    """Alumni table"""
    __tablename__ = "alumni"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    job_title = Column(String)
    has_donated = Column(Boolean)
    state = Column(String)
    company = Column(String)
