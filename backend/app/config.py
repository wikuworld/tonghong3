from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "mysql+pymysql://tonghong:tonghong_secret@127.0.0.1:3306/tonghong"
    )
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    # Auth
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60 * 12

    # Bootstrap admin (dibuat otomatis jika tabel users kosong)
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # Email (invoice reminders)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_tls: bool = True
    invoice_reminder_days_before: int = 7


settings = Settings()
