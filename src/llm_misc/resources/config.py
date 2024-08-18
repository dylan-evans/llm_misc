from pydantic import BaseModel


class DBConfig(BaseModel):
    path: str

class Config(BaseModel):
    db: DBConfig


