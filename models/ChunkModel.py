from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.chunk import Chunk
from typing import List, Dict, Any
from pymongo import ASCENDING


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNKS_NAME.value]

    async def get_next_file_index(self, project_id: str) -> int:
        """Get the next file index for a project"""
        # Find the highest file_index for this project
        pipeline = [
            {"$match": {"project_id": project_id}},
            {"$group": {"_id": None, "max_file_index": {"$max": "$file_index"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result and result[0].get("max_file_index") is not None:
            return result[0]["max_file_index"] + 1
        return 0  # First file gets index 0

    async def create_indexes(self):
        """Create database indexes for the chunks collection"""
        indexes = Chunk.get_indexes()
        for index in indexes:
            try:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False),
                    background=True
                )
            except Exception as e:
                print(f"Warning: Could not create index {index['name']}: {e}")

    async def insert_chunks(self, chunks: List[Dict[str, Any]], project_id: str = None):
        if not chunks:
            return 0
        
        # Get file index for this batch of chunks
        if project_id:
            file_index = await self.get_next_file_index(project_id)
            # Add file_index to all chunks
            for chunk in chunks:
                chunk["file_index"] = file_index
        
        # Validate and normalize via pydantic model
        docs = [Chunk(**doc).model_dump() for doc in chunks]
        result = await self.collection.insert_many(docs)
        return len(result.inserted_ids)


