from pydantic import BaseModel


class Benefactor(BaseModel):
    id: int
    first_name: str
    last_name: str
    job_title: str
    has_donated: bool
    state: str
    company: str

    class Config:
        orm_mode = True


class BenefactorIn(BaseModel):
    first_name: str = None
    last_name: str = None
    job_title: str = None
    has_donated: bool
    state: str = None
    company: str = None

    class Config:
        orm_mode = True
