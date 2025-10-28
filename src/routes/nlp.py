from fastapi import APIRouter, Response, UploadFile, File, HTTPException, Request, Depends, Form, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings
from helpers.logger import logger
import uuid
import os
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from utils.files import chunck
from utils.files.chunck import FileChunker
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from controllers import NLPController
from enums import ResponseEnum

nlp_router=APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id:str,push_request:PushRequest):

    project_model=await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    chunk_model=await ProjectModel.create_project(

    )

    project=project_model.get_project_or_create_one(
        project_id=project_id
    )

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":ResponseEnum.PROJECT_NOT_FOUND_ERROR.value
                
            }
        )
    nlp_controller=NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )

@nlp_router.post(f"/index/answer/{project_id}")
async def answer_rag(request:Request,project_id:str):
    project_model=await ProjectModel.create_instance(
        db_client=request.app.db_client

    )
    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )
    nlp_controller=NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        templete_parser=request.app.templete_parser,
    )
    answer,full_prompt,chat_history=nlp_controller.answer_rag_question(
        project=project,
        query=SearchRequest.text,
        limit=SearchRequest.limit,
    )

    if not answer:
        return JSONResponse(
            
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal":ResponseEnum.ERROR.value,
            }

        )



