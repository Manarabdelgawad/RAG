from .BaseController import BaseController
from typing import List


class NLPController(BaseController):
    def __init__(self, vectordb_client=None, generation_client=None, embedding_client=None):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}"

    # The rest of the implementation is left minimal to avoid import-time errors
    # Actual vector DB indexing should be implemented once providers are finalized




