from httpx._transports import default
from .LLMEnum import LLMEnum
class LLMFactory:
    def __init__(self,config:dict):
        self.config=config

    def create(self,provider:str):
        if provider == LLMEnum.OPENAI.value:
            return(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_char=self.config.INPUT_DEFAULT_MAX_CHAR,
                default_generation_max_output_token=self.config.GENERATION_DEFAULT_MAX_TOKEN,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        if provider == LLMEnum.COHERE.value:
             return(
                api_key=self.config.COHERE_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max_char=self.config.INPUT_DEFAULT_MAX_CHAR,
                default_generation_max_output_token=self.config.GENERATION_DEFAULT_MAX_TOKEN,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE
            )

            
        return None
