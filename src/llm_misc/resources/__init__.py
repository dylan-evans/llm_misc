
from pydantic import BaseModel, ConfigDict

from .chromadb import ChromaDBWrapper
from .config import Config


class Resources(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    config: Config
    db: ChromaDBWrapper


def get_resources(config: Config):
    return Resources(
        config=config,
        db=ChromaDBWrapper(config),
    )
