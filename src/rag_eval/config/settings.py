from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized application configuration using pydantic-settings.

    Reads from environment variables and `.env` file automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    ENV: str = Field(
        default="development",
        description="Execution environment (development, staging, production)",
    )
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Infrastructure Services (Vector DBs & Tracking)
    QDRANT_URL: str = Field(default="http://localhost:6333", description="Qdrant REST API URL")
    QDRANT_API_KEY: str | None = Field(default=None, description="Qdrant API Key")
    WEAVIATE_URL: str = Field(default="http://localhost:8080", description="Weaviate REST API URL")
    WEAVIATE_API_KEY: str | None = Field(default=None, description="Weaviate API Key")
    MLFLOW_TRACKING_URI: str = Field(
        default="http://localhost:5000", description="MLflow tracking server URI"
    )

    # AWS / Bedrock Credentials & Models
    AWS_REGION: str = Field(default="us-east-1", description="AWS Region for Bedrock calls")
    DEFAULT_EMBEDDING_PROVIDER: str = Field(
        default="bedrock", description="Default provider ('bedrock' or 'local')"
    )
    DEFAULT_EMBEDDING_MODEL: str = Field(
        default="amazon.titan-embed-text-v2:0", description="Default embedding model ID"
    )

    # Groq API Credentials & Defaults
    GROQ_API_KEY: str | None = Field(default=None, description="Groq API Key")
    GROQ_MODEL_ID: str = Field(
        default="llama-3.3-70b-versatile", description="Default Groq LLM model ID"
    )

    # Ingestion & Chunking Defaults
    DEFAULT_CHUNK_SIZE: int = Field(default=500, description="Default chunk size in characters")
    DEFAULT_CHUNK_OVERLAP: int = Field(
        default=50, description="Default chunk overlap in characters"
    )


# Global singleton instance for settings
settings = Settings()
