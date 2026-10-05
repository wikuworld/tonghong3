"""Tests for demo role user seeding."""

from unittest.mock import MagicMock, patch

from app.services.demo_users import DEMO_ROLE_USERS, ensure_demo_role_users


def test_ensure_demo_role_users_creates_missing(db_session):
    db_session.scalars.return_value.first.return_value = None

    with patch("app.services.demo_users.hash_password", return_value="hashed"):
        with patch("app.services.demo_users.settings") as mock_settings:
            mock_settings.demo_users_password = "TonghongDemo2026"
            result = ensure_demo_role_users(db_session)

    assert len(result.created) == len(DEMO_ROLE_USERS)
    assert result.skipped == []
    assert db_session.add.call_count == len(DEMO_ROLE_USERS)
    db_session.commit.assert_called_once()


def test_ensure_demo_role_users_skips_existing(db_session):
    db_session.scalars.return_value.first.return_value = MagicMock()

    with patch("app.services.demo_users.settings") as mock_settings:
        mock_settings.demo_users_password = "TonghongDemo2026"
        result = ensure_demo_role_users(db_session)

    assert result.created == []
    assert len(result.skipped) == len(DEMO_ROLE_USERS)
    db_session.commit.assert_not_called()
