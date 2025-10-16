import logging
from ...LLMInterface import LLMInterface
from ...LLMEnum import CohereEnum, DocumentEnum
import cohere


class CohereProvider(LLMInterface):

    def __init__(self,api_key:str,api_url:str|None=None,
                      defualt_input_max_char:int=50,
                      defualt_output_max_token:int=50,
                      defualt_gen_temp:float=0.1):
        self.api_key=api_key
        self.api_url=api_url
        self.defualt_input_max_char=defualt_input_max_char
        self.defualt_output_max_token=defualt_output_max_token
        self.defualt_gen_temp=defualt_gen_temp

        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None

        if self.api_url:
            self.client=cohere.Client(api_key=self.api_key, base_url=self.api_url)
        else:
            self.client=cohere.Client(api_key=self.api_key)
        
        self.logger=logging.getLogger(__name__)

    def set_generation_model(self,model_id:str):
        self.generation_model_id=model_id
    
    def set_embedding_model(self,model_id:str,embedding_size:int):
        self.embedding_model_id=model_id
        self.embedding_size=embedding_size

    def process_text(self,text:str):
        return text[:self.defualt_input_max_char].strip()
    
    def generate_text(self,prompt:str,chat_history: list|None=None,
    max_output_token:int|None=None,temperature:float|None=None):
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for cohere was not set")
            return None

        max_tokens = max_output_token if max_output_token is not None else self.defualt_output_max_token
        temperature = temperature if temperature is not None else self.defualt_gen_temp

        history = list(chat_history) if chat_history else []
        # Cohere expects chat_history as list of {role, message}
        response = self.client.chat(
            model=self.generation_model_id,
            messages=None, # not used in Cohere
            chat_history=history,
            message=self.process_text(prompt),
            temperature=temperature,
            max_tokens=max_tokens
        )

        if not response or not getattr(response, 'text', None):
            self.logger.error("Error while generating text with Cohere")
            return None
        return response.text

    def embd_text(self,text:str,document_type:str=None):
        if not self.client:
            self.logger.error("Cohere client was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for Cohere was not set")
            return None

        resp = self.client.embed(
            model=self.embedding_model_id,
            input_type=document_type if document_type else None,
            texts=[text]
        )
        if not resp or not getattr(resp, 'embeddings', None) or len(resp.embeddings)==0:
            self.logger.error("Error while embedding text with Cohere")
            return None
        return resp.text

    def embd_text(self,text:str,document_type:str=None):
        if not self.client:
            self.logger.error("cohere client was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for cohere was not set")
            return None
        input_type=CohereEnum.Document
        if document_type==DocumentEnum.QUERY:
            input_type=CohereEnum.Query

        response = self.client.embed(
            model=self.embedding_model_id,
            input_type=input_type,
            texts=[self.process_text(text)],
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with cohere")
            return None

        return response.embeddings.float[0]


    def construct_prompt(self,prompt:str,role:str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }