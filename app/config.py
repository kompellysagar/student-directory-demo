from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Student Directory API"
    database_url: str = "sqlite:///./students.db"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
