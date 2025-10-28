from pydantic import BaseModel, Field
from typing import Optional

class ProcessRequest(BaseModel):
    chunk_size:Optional[int]= 100
    overlap:Optional[int]= 20
    do_reset:Optional[int]= 0 #to understand action after this