from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from bson.objectid import ObjectId


class Chunk(BaseModel):
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    file_index: int = Field(..., ge=0)  # Index for each file added to database
    chunk_id: int = Field(..., ge=0)
    total_chunks: int = Field(..., ge=1)
    chunk_size: int = Field(..., ge=1)
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1), ("file_index", 1)],
                "name": "project_file_index_1",
                "unique": False,
            },
            {
                "key": [("filename", 1), ("file_index", 1)],
                "name": "filename_file_index_1", 
                "unique": False,
            },
            {
                "key": [("file_index", 1)],
                "name": "file_index_1",
                "unique": False,
            }
        ]


