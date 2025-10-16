from abc import ABC,abstractmethod

class LLMInterface(ABC):
    @abstractmethod #must implement function
    def set_generation_model(self,model_id:str):
        pass
    
    @abstractmethod
    def set_embedding_model(self,model_id:str,embedding_size:int|None=None):
        pass

    @abstractmethod
    def generate_text(self,prompt:str,chat_history:list|None=None,
    max_output_token:int|None=None,temperature:float|None=None):
        pass

    @abstractmethod
    def embd_text(self,text:str,document_type:str=None):
        pass

    @abstractmethod
    def construct_prompt(self,prompt:str,role:str):
        pass