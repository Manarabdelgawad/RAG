from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

def _parse_size_to_mb(value: str | int) -> int:
    """Parse env size like '10', '10MB', '5*1024*1024' into MB integer."""
    if isinstance(value, int):
        return value
    text = str(value).strip().lower()
    # Evaluate simple multiplication safely for patterns like 5*1024*1024
    if all(ch in "0123456789* " for ch in text) and "*" in text:
        parts = [p.strip() for p in text.split("*") if p.strip()]
        result = 1
        for p in parts:
            if not p.isdigit():
                raise ValueError("Invalid size expression")
            result *= int(p)
        # Convert bytes to MB if expression looks like bytes scale
        # If result is large, convert; else assume already MB
        return max(1, result // 1048576)
    # Suffix-based
    if text.endswith("mb"):
        return int(text[:-2])
    if text.endswith("m"):
        return int(text[:-1])
    if text.endswith("kb"):
        kb = int(text[:-2])
        return max(1, kb // 1024)
    if text.endswith("b"):
        b = int(text[:-1])
        return max(1, b // 1048576)
    # plain integer string -> assume MB
    return int(text)

class Settings(BaseSettings):
    # Add these required fields with default values
    ALLOWED_FILE_EXTENSIONS: list = [".pdf", ".txt", ".doc", ".docx"]
    MAX_FILE_SIZE: int = 10  # MB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_NAME: str = "rag"
    
    # Also add FILE_ALLOWED_TYPES if you're using it elsewhere
    FILE_ALLOWED_TYPES: list = [
        "application/pdf", 
        "text/plain", 
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Use the new style config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # ignore unknown env keys like app_name
    )

    @field_validator("MAX_FILE_SIZE", mode="before")
    @classmethod
    def coerce_max_file_size(cls, v):
        return _parse_size_to_mb(v)

    # Backward compatibility for older code using MONGO_DATABASE
    @property
    def MONGO_DATABASE(self) -> str:  # noqa: N802 (keep env-style name)
        return self.MONGODB_NAME

    @field_validator("MONGODB_URL", mode="before")
    @classmethod
    def normalize_mongodb_url(cls, v: str) -> str:
        if not isinstance(v, str):
            return v
        value = v.strip().strip('"').strip("'")
        if not value:
            return "mongodb://localhost:27017"
        # Fix malformed schemes like 'mongodb:localhost:27017' or 'mongodb//localhost:27017'
        if value.startswith("mongodb+srv:") and not value.startswith("mongodb+srv://"):
            value = value.replace("mongodb+srv:", "mongodb+srv://", 1)
        if value.startswith("mongodb:") and not value.startswith("mongodb://"):
            value = value.replace("mongodb:", "mongodb://", 1)
        if value.startswith("mongodb://") or value.startswith("mongodb+srv://"):
            return value
        # If no scheme provided, assume mongodb://
        if "://" not in value:
            return f"mongodb://{value}"
        return value

def get_settings() -> Settings:
    return Settings()