import os
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

class FileChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # Validate that chunk_overlap is smaller than chunk_size
        if chunk_overlap >= chunk_size:
            # Adjust chunk_overlap to be 20% of chunk_size if it's too large
            chunk_overlap = max(1, chunk_size // 5)
            print(f"Warning: chunk_overlap was too large, adjusted to {chunk_overlap}")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into chunks with metadata
        """
        if not text or text.strip() == "":
            return []
        
        # Split the text
        chunks = self.text_splitter.split_text(text)
        
        # Add metadata to each chunk
        chunk_documents = []
        for i, chunk in enumerate(chunks):
            chunk_doc = {
                "content": chunk,
                "chunk_id": i,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk),
                **metadata
            }
            chunk_documents.append(chunk_doc)
        
        return chunk_documents
    
    def chunk_file_by_lines(self, file_path: str, lines_per_chunk: int = 50) -> List[Dict]:
        """
        Chunk file by fixed number of lines
        """
        chunks = []
        current_chunk = []
        current_line_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                current_chunk.append(line)
                current_line_count += 1
                
                if current_line_count >= lines_per_chunk:
                    chunk_content = ''.join(current_chunk)
                    chunks.append({
                        "content": chunk_content,
                        "chunk_id": len(chunks),
                        "start_line": line_num - current_line_count + 1,
                        "end_line": line_num,
                        "line_count": current_line_count
                    })
                    current_chunk = []
                    current_line_count = 0
            
            # Add remaining lines as last chunk
            if current_chunk:
                chunk_content = ''.join(current_chunk)
                chunks.append({
                    "content": chunk_content,
                    "chunk_id": len(chunks),
                    "start_line": line_num - current_line_count + 1,
                    "end_line": line_num,
                    "line_count": current_line_count
                })
        
        return chunks