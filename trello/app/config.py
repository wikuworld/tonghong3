from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    cors_origins: str = "http://localhost:5173,http://localhost:8080,http://localhost:8081"

    trello_api_key: str = ""
    trello_api_secret: str = ""
    trello_access_token: str = ""
    trello_app_name: str = "Tonghong ERP"
    trello_default_board_id: str = ""
    trello_default_list_id: str = ""


settings = Settings()
