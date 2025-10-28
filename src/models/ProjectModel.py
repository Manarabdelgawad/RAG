from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.project import Project
import math
class ProjectModel(BaseDataModel):
    def __init__(self,db_client:object):
        super().__init__(db_client=db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
    
    async def get_next_project_index(self) -> int:
        """Get the next project index"""
        # Find the highest project_index
        pipeline = [
            {"$group": {"_id": None, "max_project_index": {"$max": "$project_index"}}}
        ]
        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if result and result[0].get("max_project_index") is not None:
            return result[0]["max_project_index"] + 1
        return 0  # First project gets index 0
    
    async def create_indexes(self):
        """Create database indexes for the projects collection"""
        indexes = Project.get_indexes()
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
    async def create_project(self,project_id:str):
        # Check if project already exists
        existing_project = await self.collection.find_one({"project_id": project_id})
        if existing_project:
            raise ValueError(f"Project with ID '{project_id}' already exists")
        
        project_index = await self.get_next_project_index()
        project=Project(project_id=project_id, project_index=project_index)
        await self.collection.insert_one(project.model_dump())
        return project
    async def get_project_or_create_one(self,project_id:str):
        record=await self.collection.find_one(
            {"project_id":project_id})
        if record is None:
            project=await self.create_project(project_id)
            return project
        else:
            return record
    
    async def get_all_project(self,page:int=1,page_size:int=10):
        # count total number of documents 
        total_documents=await self.collection.count_documents({})
        # calculate total pages
        total_pages=math.ceil(total_documents/page_size)

        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)
        projects=[]
        async for document in cursor:
            projects.append(Project(**document))
        return projects,total_pages
        



    