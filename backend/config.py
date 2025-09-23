from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    GOOGLE_API_KEY: SecretStr
    DATABASE_URL: str
    SECRET_KEY: SecretStr
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        
        
        
settings = AppSettings()