"""Klien HTTP untuk Trello REST API v1."""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import quote, urlencode

import httpx

from app.config import settings

TRELLO_API_BASE = "https://api.trello.com/1"
TRELLO_AUTH_BASE = "https://trello.com/1"


class TrelloConfigError(RuntimeError):
    """Kredensial Trello belum lengkap."""


class TrelloApiError(RuntimeError):
    """Trello API mengembalikan respons gagal."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Trello API {status_code}: {detail}")


class TrelloClient:
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        api_secret: Optional[str] = None,
        app_name: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = (api_key if api_key is not None else settings.trello_api_key).strip()
        self.access_token = (
            access_token if access_token is not None else settings.trello_access_token
        ).strip()
        self.api_secret = (
            api_secret if api_secret is not None else settings.trello_api_secret
        ).strip()
        self.app_name = (app_name if app_name is not None else settings.trello_app_name).strip()
        self.timeout = timeout

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def is_connected(self) -> bool:
        return bool(self.api_key and self.access_token)

    def authorize_url(
        self,
        *,
        scope: str = "read,write",
        expiration: str = "never",
        response_type: str = "token",
    ) -> str:
        if not self.api_key:
            raise TrelloConfigError("TRELLO_API_KEY belum diisi")
        params = {
            "expiration": expiration,
            "name": self.app_name or "Tonghong ERP",
            "scope": scope,
            "response_type": response_type,
            "key": self.api_key,
        }
        return f"{TRELLO_AUTH_BASE}/authorize?{urlencode(params)}"

    def _auth_params(self) -> dict[str, str]:
        if not self.api_key:
            raise TrelloConfigError("TRELLO_API_KEY belum diisi")
        if not self.access_token:
            raise TrelloConfigError(
                "TRELLO_ACCESS_TOKEN belum diisi. "
                "Buka /api/v1/trello/authorize-url untuk OAuth."
            )
        return {"key": self.api_key, "token": self.access_token}

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_body: Optional[dict[str, Any]] = None,
    ) -> Any:
        auth = self._auth_params()
        query = {**(params or {}), **auth}
        url = f"{TRELLO_API_BASE}{path}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(method, url, params=query, json=json_body)
        if response.status_code >= 400:
            detail = response.text.strip() or response.reason_phrase
            raise TrelloApiError(response.status_code, detail)
        if not response.content:
            return None
        return response.json()

    def get_me(self) -> dict[str, Any]:
        return self._request("GET", "/members/me")

    def list_boards(self, *, filter_open: bool = True) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"fields": "name,url,closed"}
        if filter_open:
            params["filter"] = "open"
        return self._request("GET", "/members/me/boards", params=params)

    def list_board_lists(self, board_id: str) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            f"/boards/{quote(board_id, safe='')}/lists",
            params={"fields": "name,closed", "filter": "open"},
        )

    def list_cards(self, list_id: str) -> list[dict[str, Any]]:
        return self._request(
            "GET",
            f"/lists/{quote(list_id, safe='')}/cards",
            params={"fields": "name,desc,url,shortUrl,idList,closed"},
        )

    def create_card(
        self,
        *,
        list_id: str,
        name: str,
        desc: str = "",
        id_labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "idList": list_id,
            "name": name,
            "desc": desc,
        }
        if id_labels:
            body["idLabels"] = ",".join(id_labels)
        return self._request("POST", "/cards", params=body)

    def update_card(
        self,
        card_id: str,
        *,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        id_list: Optional[str] = None,
        closed: Optional[bool] = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if desc is not None:
            params["desc"] = desc
        if id_list is not None:
            params["idList"] = id_list
        if closed is not None:
            params["closed"] = str(closed).lower()
        return self._request("PUT", f"/cards/{quote(card_id, safe='')}", params=params)
