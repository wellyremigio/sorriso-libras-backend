from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "Sorriso Libras API"
    mongodb_uri: str = ""
    database_name: str = "sorriso_libras_db"
    
    model_config = SettingsConfigDict (
        env_file = ".env",
        env_file_encoding="utf-8"
    )
    
@lru_cache
def get_settings () -> Settings:
    settings = Settings()

    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI não foi configurada.")

    return settings
