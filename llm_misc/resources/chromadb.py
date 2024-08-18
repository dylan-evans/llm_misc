

from chromadb import PersistentClient

from .config import Config


class ChromaDBWrapper:
    def __init__(self, config: Config):
        self.client = PersistentClient(path=config.db.path)

    def get_collection(self, name):
        return self.client.get_or_create_collection(name)
