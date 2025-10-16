from fastapi import UploadFile
from controllers.BaseController import BaseController
from helpers.config import get_settings
from enums.ResponseEnum import ResponseEnum
import logging
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576
        self.settings = get_settings()  # Add this line
    
    async def validate_upload(self, file: UploadFile):
        if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
            return False, ResponseEnum.ERROR

        # Read file to check size
        content = await file.read()
        file_size = len(content)

        # Reset file pointer for later use
        await file.seek(0)

        if file_size > self.settings.MAX_FILE_SIZE * self.size_scale:
            return False, ResponseEnum.ERROR

        return True, ResponseEnum.SUCCESS
        