import logging
from ...LLMInterface import LLMInterface
from ...LLMEnum import OpenAIEnum
from openai import OpenAI

class OpenaiProvider(LLMInterface):

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

        # OpenAI SDK uses base_url instead of api_url; only set if provided
        if self.api_url:
            self.client=OpenAI(api_key=self.api_key, base_url=self.api_url)
        else:
            self.client=OpenAI(api_key=self.api_key)
         
        self.logger=logging.getLogger(__name__)

    def set_generation_model(self,model_id:str):
        self.generation_model_id=model_id
    
    def set_embedding_model(self,model_id:str,embedding_size:int):
        self.embedding_model_id=model_id
        self.embedding_size=embedding_size
    
    def generate_text(self,prompt:str,chat_history: list|None=None,
    max_output_token:int|None=None,temperature:float|None=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for openAI was not set")
            return None

        max_tokens = max_output_token if max_output_token is not None else self.defualt_output_max_token
        temperature = temperature if temperature is not None else self.defualt_gen_temp
        messages = list(chat_history) if chat_history else []
        messages.append(self.construct_prompt(prompt=prompt,role=OpenAIEnum.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        if not response or not getattr(response, 'choices', None) or len(response.choices)==0 or not response.choices[0]:
            self.logger.error("Error while generating text with OpenAI")
            return None
        # OpenAI Chat Completions returns string content
        return response.choices[0].message.content
         

    def embd_text(self,text:str,document_type:str=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for openAI was not set")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=text,
        )

        if not response or not getattr(response, 'data', None) or len(response.data)==0 or not getattr(response.data[0], 'embedding', None):
            self.logger.error("Error while embedding text with openai")
            return None

        return response.data[0].embedding

    def construct_prompt(self,prompt:str,role:str):
        return {
            "role": role,
            "content": self.process_text(prompt)
        }

    def process_text(self,text:str):
        return text[:self.defualt_input_max_char].strip()

 


       




        
    
