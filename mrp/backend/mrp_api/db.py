from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from mrp_api.config import settings
from mrp_api.timeutil import mariadb_time_zone_offset

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _set_session_timezone(dbapi_connection, _connection_record) -> None:
    tz = mariadb_time_zone_offset()
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute(f"SET time_zone = '{tz}'")
    finally:
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_identity_tables() -> None:
    """Buat tabel identitas MRP di uat_tonghong_mrp tanpa Alembic ERP."""
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS mrp_users (
                  id BIGINT AUTO_INCREMENT PRIMARY KEY,
                  username VARCHAR(80) NOT NULL UNIQUE,
                  password_hash VARCHAR(255) NOT NULL,
                  role VARCHAR(32) NOT NULL DEFAULT 'operator',
                  is_active TINYINT(1) NOT NULL DEFAULT 1,
                  department VARCHAR(50) NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME NULL
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS mrp_role_permissions (
                  id BIGINT AUTO_INCREMENT PRIMARY KEY,
                  role VARCHAR(32) NOT NULL,
                  module_key VARCHAR(80) NOT NULL,
                  action VARCHAR(32) NOT NULL,
                  allowed TINYINT(1) NOT NULL DEFAULT 1,
                  UNIQUE KEY uq_mrp_role_permissions_key (role, module_key, action)
                )
                """
            )
        )
