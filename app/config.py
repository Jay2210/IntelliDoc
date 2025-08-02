from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PINECONE_API_KEY: str
    GEMINI_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    PINECONE_ENV: str
    S3_BUCKET: str
    AWS_REGION: str
    JINA_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
