from pydantic import BaseModel,Field, validator
from typing import Optional
from bson.objectid import ObjectId
class Project(BaseModel):
    _id: Optional[ObjectId]
    project_id: str=Field(...,min_length=1)
    project_index: int = Field(..., ge=0)  # Sequential index for each project
    
    @validator("project_id")
    def validate_project_id(cls, value):
        if not value or not value.strip():
            raise ValueError("Project ID cannot be empty")
        return value.strip()

    class Config:
        arbitrary_types_allowed=True
    
    @classmethod
    def get_indexes(cls):
        return[
            {
                "key": [("project_id",1)],
                "name": "project_id_1",
                "unique": True,
            },
            {
                "key": [("project_index",1)],
                "name": "project_index_1",
                "unique": True,
            }
        ]
    

