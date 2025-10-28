from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
from models.ProjectModel import ProjectModel
from helpers.logger import logger

project_router = APIRouter(prefix="/api/projects", tags=["projects"])

class CreateProjectRequest(BaseModel):
    project_id: str = Field(..., min_length=1, description="Unique project identifier")

class ProjectResponse(BaseModel):
    project_id: str
    project_index: int
    message: str

@project_router.post("/create", response_model=ProjectResponse)
async def create_project(request: Request, project_data: CreateProjectRequest):
    """Create a new project with the specified ID and automatic index assignment"""
    try:
        mongodb_client = request.app.mongodb_client
        project_model = ProjectModel(db_client=mongodb_client)
        
        # Create the project with the specified ID (this will automatically assign a project_index)
        project = await project_model.create_project(project_data.project_id)
        
        logger.info(f"Project created: {project_data.project_id} with index {project.project_index}")
        
        return ProjectResponse(
            project_id=project.project_id,
            project_index=project.project_index,
            message="Project created successfully"
        )
        
    except ValueError as e:
        # Handle case where project already exists
        logger.warning(f"Project creation failed - project exists: {str(e)}")
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Project creation failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Project creation failed: {str(e)}")

@project_router.post("/get-or-create", response_model=ProjectResponse)
async def get_or_create_project(request: Request, project_data: CreateProjectRequest):
    """Get existing project or create new one with the specified ID"""
    try:
        mongodb_client = request.app.mongodb_client
        project_model = ProjectModel(db_client=mongodb_client)
        
        # Get existing project or create new one
        project = await project_model.get_project_or_create_one(project_data.project_id)
        
        logger.info(f"Project retrieved/created: {project_data.project_id} with index {project.get('project_index', 0)}")
        
        return ProjectResponse(
            project_id=project["project_id"],
            project_index=project.get("project_index", 0),
            message="Project retrieved or created successfully"
        )
        
    except Exception as e:
        logger.error(f"Project get-or-create failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Project get-or-create failed: {str(e)}")

@project_router.get("/list")
async def list_projects(request: Request, page: int = 1, page_size: int = 10):
    """List all projects with pagination"""
    try:
        mongodb_client = request.app.mongodb_client
        project_model = ProjectModel(db_client=mongodb_client)
        
        projects, total_pages = await project_model.get_all_project(page, page_size)
        
        return {
            "projects": [
                {
                    "project_id": project.project_id,
                    "project_index": project.project_index
                } for project in projects
            ],
            "total_pages": total_pages,
            "current_page": page
        }
        
    except Exception as e:
        logger.error(f"Failed to list projects: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to list projects: {str(e)}")

@project_router.get("/{project_id}")
async def get_project(request: Request, project_id: str):
    """Get a specific project by ID"""
    try:
        mongodb_client = request.app.mongodb_client
        project_model = ProjectModel(db_client=mongodb_client)
        
        project = await project_model.get_project_or_create_one(project_id)
        
        return {
            "project_id": project["project_id"],
            "project_index": project.get("project_index", 0)
        }
        
    except Exception as e:
        logger.error(f"Failed to get project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Failed to get project: {str(e)}")
