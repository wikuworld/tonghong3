"""API Trello untuk dev todo / review — tanpa auth Tonghong."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.client import TrelloApiError, TrelloClient, TrelloConfigError
from app.service import TrelloService

router = APIRouter(prefix="/trello", tags=["trello"])


class TrelloCreateCardIn(BaseModel):
    list_id: Optional[str] = None
    name: str = Field(min_length=1, max_length=500)
    desc: str = ""


def _handle_errors(exc: Exception) -> HTTPException:
    if isinstance(exc, TrelloConfigError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, TrelloApiError):
        return HTTPException(status_code=502, detail=exc.detail)
    raise exc


@router.get("/status")
def trello_status() -> dict[str, Any]:
    return TrelloService().status()


@router.get("/authorize-url")
def trello_authorize_url() -> dict[str, str]:
    client = TrelloClient()
    try:
        return {
            "authorize_url": client.authorize_url(),
            "hint": (
                "Buka URL di browser, izinkan akses, salin token dari URL "
                "(setelah #token=) ke TRELLO_ACCESS_TOKEN di .env lalu restart service trello."
            ),
        }
    except TrelloConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/me")
def trello_me() -> dict[str, Any]:
    try:
        return TrelloClient().get_me()
    except (TrelloConfigError, TrelloApiError) as exc:
        raise _handle_errors(exc) from exc


@router.get("/boards")
def trello_boards() -> list[dict[str, Any]]:
    try:
        return TrelloClient().list_boards()
    except (TrelloConfigError, TrelloApiError) as exc:
        raise _handle_errors(exc) from exc


@router.get("/boards/{board_id}/lists")
def trello_board_lists(board_id: str) -> list[dict[str, Any]]:
    try:
        return TrelloClient().list_board_lists(board_id)
    except (TrelloConfigError, TrelloApiError) as exc:
        raise _handle_errors(exc) from exc


@router.get("/lists/{list_id}/cards")
def trello_list_cards(list_id: str) -> list[dict[str, Any]]:
    try:
        return TrelloClient().list_cards(list_id)
    except (TrelloConfigError, TrelloApiError) as exc:
        raise _handle_errors(exc) from exc


@router.post("/cards")
def trello_create_card(body: TrelloCreateCardIn) -> dict[str, Any]:
    try:
        if body.list_id:
            return TrelloClient().create_card(
                list_id=body.list_id,
                name=body.name,
                desc=body.desc,
            )
        return TrelloService().create_todo_card(name=body.name, desc=body.desc)
    except (TrelloConfigError, TrelloApiError) as exc:
        raise _handle_errors(exc) from exc
