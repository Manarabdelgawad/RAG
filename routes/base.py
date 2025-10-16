from fastapi import FastAPI,APIRouter,Depends
import os
from helpers.config import get_settings


base_router=APIRouter(
    prefix="/api/v1",
    tags=["Base"]
)

@base_router.get("/")
def welcome():
    app_settings=get_settings()
    return{"message":"Welcome to FastAPI"}

#upload file endpoint
