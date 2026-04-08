from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "mysql+pymysql://tonghong:tonghong_secret@127.0.0.1:3306/tonghong"
    )
    cors_origins: str = "http://localhost:5173,http://localhost:8080"


settings = Settings()
