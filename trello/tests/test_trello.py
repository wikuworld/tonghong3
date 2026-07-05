"""Unit test untuk stack Trello (dev todo / review)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.client import TrelloClient, TrelloConfigError
from app.service import TrelloService


def test_trello_client_requires_api_key_for_authorize_url():
    client = TrelloClient(api_key="", access_token="")
    with pytest.raises(TrelloConfigError):
        client.authorize_url()


def test_trello_client_authorize_url_contains_key():
    client = TrelloClient(api_key="abc123", access_token="", api_secret="secret")
    url = client.authorize_url()
    assert "key=abc123" in url
    assert "trello.com/1/authorize" in url


def test_trello_service_status_payload():
    body = TrelloService().status()
    assert "configured" in body
    assert "connected" in body
    assert "default_board_id" in body
    assert "tonghong_api_url" not in body


@patch("app.service.TrelloClient")
def test_create_todo_card_uses_default_list(mock_client_cls):
    mock_client = MagicMock()
    mock_client.create_card.return_value = {"id": "c1", "url": "https://trello.com/c/c1"}
    mock_client_cls.return_value = mock_client

    with patch("app.service.settings") as mock_settings:
        mock_settings.trello_default_list_id = "list123"
        result = TrelloService(client=mock_client).create_todo_card(name="Review PO form")

    mock_client.create_card.assert_called_once_with(list_id="list123", name="Review PO form", desc="")
    assert result["card_id"] == "c1"


@patch("app.client.httpx.Client")
def test_trello_client_get_me(mock_client_cls):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"username":"tester"}'
    mock_response.json.return_value = {"username": "tester"}
    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.request.return_value = mock_response
    mock_client_cls.return_value = mock_client

    result = TrelloClient(api_key="key", access_token="token").get_me()
    assert result["username"] == "tester"
