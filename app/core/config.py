from __future__ import annotations
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class AppSettings(BaseSettings):
    # Server settings
    port: int = Field(default=8002, env="PORT")
    
    # Groq API settings
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", env="GROQ_BASE_URL")
    default_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_DEFAULT_MODEL")
    request_timeout_s: float = Field(30.0, env="REQUEST_TIMEOUT_S")
    max_retries: int = Field(2, env="HTTP_MAX_RETRIES")
    
    # CORS settings
    enable_cors: bool = Field(True, env="ENABLE_CORS")
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    
    # MongoDB settings
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    mongodb_database: str = Field(default="harmonizacao", env="MONGODB_DATABASE")
    mongodb_collection_clientes: str = Field(default="clientes", env="MONGODB_COLLECTION_CLIENTES")

    # RAG Settings
    # Embedding service configuration
    embedding_service_type: str = Field(default="sentence_transformer", env="EMBEDDING_SERVICE_TYPE")
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Vector store configuration
    vector_store_type: str = Field(default="chroma", env="VECTOR_STORE_TYPE")
    vector_store_path: str = Field(default="./data/vectorstore", env="VECTOR_STORE_PATH")
    chroma_collection_name: str = Field(default="harmonizacao_docs", env="CHROMA_COLLECTION_NAME")
    
    # Document processing settings
    default_chunk_size: int = Field(default=1000, env="DEFAULT_CHUNK_SIZE")
    default_chunk_overlap: int = Field(default=200, env="DEFAULT_CHUNK_OVERLAP")
    default_chunking_strategy: str = Field(default="recursive", env="DEFAULT_CHUNKING_STRATEGY")
    
    # Retrieval settings
    default_max_results: int = Field(default=5, env="DEFAULT_MAX_RESULTS")
    default_min_score: float = Field(default=0.3, env="DEFAULT_MIN_SCORE")
    
    # File upload settings
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_file_extensions: List[str] = Field(
        default_factory=lambda: [".txt", ".md", ".pdf", ".docx", ".doc"],
        env="ALLOWED_FILE_EXTENSIONS"
    )

    # Kafka settings
    kafka_enabled: bool = Field(default=False, env="KAFKA_ENABLED")
    kafka_bootstrap_servers: str = Field(default="localhost:19092", env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_topic_cliente: str = Field(default="clientes", env="KAFKA_TOPIC_CLIENTE")

    @field_validator("cors_allow_origins", mode="before")
    def parse_cors_allow_origins(cls, v: Union[str, List[str], None]) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [i.strip() for i in v.split(",")]
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("allowed_file_extensions", mode="before")
    def parse_allowed_extensions(cls, v: Union[str, List[str], None]) -> List[str]:
        if v is None:
            return [".txt", ".md", ".pdf", ".docx", ".doc"]
        if isinstance(v, str):
            extensions = [ext.strip() for ext in v.split(",") if ext.strip()]
            # Ensure extensions start with dot
            return [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",  # Para evitar erro com variáveis extras no .env
    }

settings = AppSettings()