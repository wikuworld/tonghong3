"""Helper ringan untuk board Trello (dev todo / review)."""

from __future__ import annotations

from typing import Any, Optional

from app.client import TrelloClient, TrelloConfigError
from app.config import settings


class TrelloService:
    def __init__(self, client: Optional[TrelloClient] = None) -> None:
        self.client = client or TrelloClient()

    def status(self) -> dict[str, Any]:
        return {
            "configured": self.client.is_configured,
            "connected": self.client.is_connected,
            "default_board_id": settings.trello_default_board_id or None,
            "default_list_id": settings.trello_default_list_id or None,
            "app_name": self.client.app_name,
        }

    def resolve_list_id(self, list_id: Optional[str] = None) -> str:
        resolved = (list_id or settings.trello_default_list_id or "").strip()
        if not resolved:
            raise TrelloConfigError(
                "List Trello belum ditentukan. "
                "Kirim list_id atau set TRELLO_DEFAULT_LIST_ID."
            )
        return resolved

    def create_todo_card(
        self,
        *,
        name: str,
        desc: str = "",
        list_id: Optional[str] = None,
    ) -> dict[str, Any]:
        target_list = self.resolve_list_id(list_id)
        card = self.client.create_card(list_id=target_list, name=name, desc=desc)
        return {
            "card_id": card.get("id"),
            "card_url": card.get("url") or card.get("shortUrl"),
            "list_id": target_list,
        }
