from enum import Enum

class LLMEnum(Enum):
    OPENAI="OPENAI"
    COHERE="COHERE"
    OLLAMA="OLLAMA"

class OpenAIEnum(Enum):
    SYSTEM="system"
    USER="user"
    ASSISTANT="assistant"

class CohereEnum(Enum):
    SYSTEM="SYSTEM",
    USER="USER",
    ASSISTANT="CHATBOT"
    Document="search_document"
    Query="search_query"


class DocumentEnum(Enum):
    DOCUMENT="document"
    QUERY="query"