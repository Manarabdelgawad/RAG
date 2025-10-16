from .BaseController import BaseController
from routes.schemes.data import ProcessRequest  # ✅ Fixed typo
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from fastapi import UploadFile
import os
import shutil

class ProcessController(BaseController):
    def __init__(self):
        super().__init__()
        self.project_controller = ProjectController()
        self.upload_folder = 'uploads'
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        allowed_extensions = {'.txt', '.pdf'}
        _, ext = os.path.splitext(filename)
        return ext.lower() in allowed_extensions
    
    def save_file(self, file: UploadFile, file_path: str):
        """Save uploaded file to disk"""
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    async def process_file(self, file: UploadFile, process_request: ProcessRequest):  # ✅ Added async
        if not self.allowed_file(file.filename):  # ✅ Use self.allowed_file
            return {"error": "File type not allowed"}
        
        file_path = os.path.join(self.upload_folder, file.filename)
        self.save_file(file, file_path)  # ✅ Use self.save_file
        
        try:
            if file.filename.endswith('.txt'):
                loader = TextLoader(file_path, encoding='utf-8')
            elif file.filename.endswith('.pdf'):
                loader = PyMuPDFLoader(file_path)
            else:
                return {"error": "Unsupported file type"}
            
            documents = loader.load()
            text_splitter = CharacterTextSplitter(
                chunk_size=process_request.chunk_size, 
                chunk_overlap=process_request.overlap
            )
            docs = text_splitter.split_documents(documents)
            
            project_id = self.project_controller.get_current_project_id()
            if process_request.do_reset:
                self.project_controller.reset_project_data(project_id)
            
            self.project_controller.add_documents_to_project(project_id, docs)
            
            # Clean up uploaded file after processing
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return {"message": f"Processed {len(docs)} document chunks"}
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            return {"error": f"Processing failed: {str(e)}"}