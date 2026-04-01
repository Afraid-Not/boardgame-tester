from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# 프로젝트 루트의 .env 참조
_env_path = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    openai_api_key: str = ""
    ngrok_auth_token: str = ""

    class Config:
        env_file = str(_env_path)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
