from multiprocessing import Value
from pymongo.typings import _DocumentType
from qdrant_client.grpc import Document, RetrievedPoint

from stores.llm.templetes.locales.ar.rag import document_prompt, footer_prompt, system_prompt
from .BaseController import BaseController
from models.db_schemes import Project,chunk
from stores.llm.LLMEnum import  OpenAIEnum,CohereEnum,DocumentEnum

from typing import List

class NLPController(BaseController):
    def __init__(self,vectordb_client,generation_client,ebedding_client):
        super().__init__()

        self.vectordb_client=vectordb_client
        self.generation_client=generation_client
        self.ebedding_client=ebedding_client

    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}"

    def reset_vector_db_collection(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        collection_info= self.vectordb_client.get_collection_info(collection_name=collection_name)

        return collection_info

    def index_into_vector_db(self,project:Project,chunks:List[chunk],do_reset:bool=False):
        # step 1 : get collection name
        collection_name=self.create_collection_name(project_id=project.project_id)
        # step 2 :manage item
        texts=[c.chunk_text for c in chunks]
        metadata=[c.chunk_metadata for c in chunks]
        vectors=[
            self.ebedding_client.embed_text(text=text,document_type=DocumentTypeEnum.DOCUMENT.VALUE)
            for text in texts
        ]

        # step 3 :create collection if not exists
        _=self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset
        )
        # step 4 :insert into vector db
        _=self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors
        )
        return True

    def search_vector_db_collection(self,project:Project,text:str,limit:int=10):

        collection_name=self.create_collection_name(project_id=project.project_id)

        vector=self.embedding_client.embed_text(text=text,document_type=_DocumentTypeEnum=QUERY.Value)

        if not vector or len(vector)==0:
         return False

        results=self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )
        if not results:
            return False
        return results

    def answer_rag_question(self,project:Project,query:str,limit:int=10):

        answer,full_prompt,chat_history=None,None,None

        # step1: retriave related documents
        retrieved_document=self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_document or len(retrieved_document)==0:
            return answer,full_prompt,chat_history

        # step2: construct llm prompt
        system_prompt=self.templete_parser.get("rag","system_prompt")

        

        document_prompt="/n".join([ 
            self.template_parser.get("rag","document_prompt",{
                "doc_num":idx+1,
                "chunk_text":doc.text,
                }
                )
            for idx,doc in enumerate(retrieved_document)
        ])

        footer_prompt=self.templete_parser.get("rag","footer_prompt")

        chat_history=[
            self.generation_client.costruct(
                prompt=system_prompt,
                role=self.generation_client.enums.value,

            )
        ]

        full_prompt="/n/n".join([document_prompt,footer_prompt])

        answer=self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer,full_prompt,chat_history










