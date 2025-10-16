from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends, Form
from helpers.config import get_settings
from helpers.logger import logger
import uuid
import os
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from utils.files.chunck import FileChunker
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

data_router = APIRouter(prefix="/api/data", tags=["data"])
settings = get_settings()

class ProcessChunkRequest(BaseModel):
    filename: str
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200

class FileUploadResponse(BaseModel):
    message: str
    filename: str
    project_id: str
    file_path: str

class ChunkProcessResponse(BaseModel):
    message: str
    chunks_created: int
    project_id: str
    filename: str

@data_router.post("/uploadfile", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...), 
    project_id: str = Form(...)
):
    """Upload file with project ID association"""
    try:
        # Validate file type
        if file.content_type not in settings.FILE_ALLOWED_TYPES:
            logger.error(f"Invalid file type: {file.filename} - {file.content_type}")
            raise HTTPException(400, "File type not supported")
        
        # Validate file size
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE * 1048576:
            logger.error(f"File too large: {file.filename} - {len(content)} bytes")
            raise HTTPException(400, "File too large")
        
        # Generate random filename with project prefix
        random_name = f"{project_id}_{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}"
        file_location = f"uploads/{random_name}"
        
        # Save file
        os.makedirs("uploads", exist_ok=True)
        with open(file_location, "wb") as f:
            f.write(content)
        
        logger.info(f"Upload success: {file.filename} -> {random_name} for project {project_id}")
        
        return FileUploadResponse(
            message="File uploaded successfully",
            filename=random_name,
            project_id=project_id,
            file_path=file_location
        )
        
    except HTTPException:
        raise  # User-friendly errors
    except Exception as e:
        logger.error(f"Upload failed: {file.filename} - {str(e)}", exc_info=True)
        raise HTTPException(500, "Upload failed")


@data_router.post("/process-chunks/{project_id}", response_model=ChunkProcessResponse)
async def process_chunks(project_id: str, request: Request, chunk_request: ProcessChunkRequest):
    """Process uploaded file into chunks and store in database"""
    try:
        # Check if file exists
        file_path = f"uploads/{chunk_request.filename}"
        if not os.path.exists(file_path):
            raise HTTPException(404, f"File not found: {chunk_request.filename}")
        
        # Read file content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        
        if not text.strip():
            raise HTTPException(400, "File is empty or contains no readable text")
        
        # Chunk the text
        chunker = FileChunker(
            chunk_size=chunk_request.chunk_size, 
            chunk_overlap=chunk_request.chunk_overlap
        )
        metadata = {
            "project_id": project_id, 
            "filename": chunk_request.filename
        }
        chunk_dicts = chunker.chunk_text(text=text, metadata=metadata)

        # Save to MongoDB using app client
        mongodb_client = request.app.mongodb_client
        chunk_model = ChunkModel(db_client=mongodb_client)
        inserted_count = await chunk_model.insert_chunks(chunk_dicts, project_id)

        logger.info(f"Processed {inserted_count} chunks for file {chunk_request.filename} in project {project_id}")
        
        return ChunkProcessResponse(
            message="Chunks processed and stored successfully",
            chunks_created=inserted_count,
            project_id=project_id,
            filename=chunk_request.filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chunk processing failed: {chunk_request.filename} - {str(e)}", exc_info=True)
        raise HTTPException(500, f"Chunk processing failed: {str(e)}")

@data_router.post("/upload-and-chunk")
async def upload_and_chunk(request: Request, file: UploadFile = File(...), project_id: str = Form("default")):
    """Legacy endpoint - upload and chunk in one step"""
    try:
        # Validate file type
        if file.content_type not in settings.FILE_ALLOWED_TYPES:
            logger.error(f"Invalid file type: {file.filename} - {file.content_type}")
            raise HTTPException(400, "File type not supported")

        # Read content in memory (bounded by MAX_FILE_SIZE)
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE * 1048576:
            logger.error(f"File too large: {file.filename} - {len(content)} bytes")
            raise HTTPException(400, "File too large")

        text = content.decode("utf-8", errors="ignore")

        # Chunk the text
        chunker = FileChunker(chunk_size=1000, chunk_overlap=200)
        metadata = {"project_id": project_id, "filename": file.filename}
        chunk_dicts = chunker.chunk_text(text=text, metadata=metadata)

        # Save to MongoDB using app client
        mongodb_client = request.app.mongodb_client
        chunk_model = ChunkModel(db_client=mongodb_client)
        inserted_count = await chunk_model.insert_chunks(chunk_dicts, project_id)

        return {"message": "Chunks stored", "chunks": inserted_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload-and-chunk failed: {file.filename} - {str(e)}", exc_info=True)
        raise HTTPException(500, "Upload and chunk failed")