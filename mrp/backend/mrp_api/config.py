from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "dev"
    database_url: str = (
        "mysql+pymysql://uat_tonghong_mrp:UatTonghongMrp2026@127.0.0.1:3306/uat_tonghong_mrp"
    )
    erp_api_url: str = "http://127.0.0.1:8001"
    erp_service_token: str = "dev-erp-service-token-change-me"
    cors_origins: str = (
        "http://localhost:8082,http://127.0.0.1:8082,"
        "http://localhost:8081,http://127.0.0.1:8081"
    )

    jwt_secret: str = "dev-mrp-secret-change-me"
    mrp_jwt_secret: str = "dev-mrp-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60 * 12
    jwt_issuer: str = "tonghong-mrp"
    jwt_audience: str = "mrp"

    admin_username: str = "admin"
    admin_password: str = "admin123"
    demo_users_password: str = "TonghongDemo2026"

    app_timezone: str = "Asia/Jakarta"
    mrp_api_port: int = 8002


settings = Settings()
