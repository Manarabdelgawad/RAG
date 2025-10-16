from helpers.config import get_settings
from fastapi import FastAPI,APIRouter
import os
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()

    def get_database_path(self,db_name:str):
        database_path=os.path.join(
        self.database_dir,db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)
        
        return database_path
        