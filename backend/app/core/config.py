from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "claude-harness-todo"
    MONGODB_URL: str = "mongodb://mongo:27017"
    DATABASE_NAME: str = "harness_db"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
