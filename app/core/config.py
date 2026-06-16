from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://jeoksan:jeoksan@localhost:5432/jeoksan"
    app_port: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()
정