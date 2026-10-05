"""Shared helpers for FastAPI HTTP integration tests."""

from dataclasses import dataclass
from typing import Any, Callable, Optional

from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app
from app.routers.auth import get_current_user


class DummyDbSession:
    """Minimal DB stub — override ``get`` / ``scalars`` per test."""

    def __init__(
        self,
        *,
        get_handler: Optional[Callable[[Any, int], Any]] = None,
        scalars_handler: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        self._get_handler = get_handler
        self._scalars_handler = scalars_handler

    def get(self, model: Any, obj_id: int) -> Any:
        if self._get_handler:
            return self._get_handler(model, obj_id)
        return None

    def scalars(self, _stmt: Any) -> Any:
        if self._scalars_handler:
            return self._scalars_handler(_stmt)

        class _Empty:
            def first(self) -> None:
                return None

            def all(self) -> list:
                return []

        return _Empty()


@dataclass
class DummyUser:
    username: str
    role: str
    is_active: bool = True


def make_api_client(db: Optional[DummyDbSession] = None) -> TestClient:
    session = db if db is not None else DummyDbSession()

    def _override_db():
        yield session

    app.dependency_overrides[get_db] = _override_db
    return TestClient(app)


def set_auth_user(role: str, username: str = "tester") -> None:
    app.dependency_overrides[get_current_user] = lambda: DummyUser(
        username=username,
        role=role,
    )


def clear_auth_user() -> None:
    app.dependency_overrides.pop(get_current_user, None)


def clear_api_overrides() -> None:
    app.dependency_overrides.clear()


def assert_status(
    client: TestClient,
    method: str,
    path: str,
    expected: int,
    payload: Any = None,
    *,
    params: Optional[dict] = None,
) -> None:
    req = getattr(client, method.lower())
    kwargs: dict[str, Any] = {}
    if params is not None:
        kwargs["params"] = params
    if payload is not None:
        kwargs["json"] = payload
    resp = req(path, **kwargs)
    assert resp.status_code == expected, (
        f"{method} {path} expected {expected}, got {resp.status_code}: {resp.text}"
    )
