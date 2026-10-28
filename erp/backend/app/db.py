from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config import settings
from app.timeutil import mariadb_time_zone_offset

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"charset": "utf8mb4"},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _set_session_timezone(dbapi_connection, _connection_record) -> None:
    """Samakan session MariaDB dengan zona aplikasi (GMT+7)."""
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
