from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel

nlp_router=APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

class PushRequest(BaseModel):
    reset: bool = Field(default=False, description="Reset vector DB collection before indexing")

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    try:
        # Normalize incoming project_id (avoid trailing newlines/spaces)
        project_id = project_id.strip()
        mongodb_client = request.app.mongodb_client
        project_model = ProjectModel(db_client=mongodb_client)
        chunk_model = ChunkModel(db_client=mongodb_client)

        project = await project_model.get_project_or_create_one(project_id=project_id)
        if not project:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": "project_not_found"}
            )

        # Count existing chunk documents for this project as inserted count placeholder
        inserted_item_count = await chunk_model.collection.count_documents({"project_id": project_id})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": "insert into vectordb success",
                "project_id": project_id,
                "reset": push_request.reset,
                "inserted_item_count": inserted_item_count
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    