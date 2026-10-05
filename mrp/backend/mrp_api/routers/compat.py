from fastapi import APIRouter, Depends

from mrp_api.routers.auth import SHOPFLOOR_ROLES, get_current_user
from mrp_api.models import MrpUser

router = APIRouter(tags=["compat"])


def _matrix():
    roles = list(SHOPFLOOR_ROLES)
    return {
        "matrix": {
            "dashboard": {
                "view": roles,
            },
            "inventory": {
                "view": roles,
                "create": roles,
                "update": roles,
            },
            "mrpShopfloor": {
                "view": roles,
                "create": roles,
                "update": roles,
            },
        }
    }


@router.get("/permissions/matrix")
def permission_matrix(_user: MrpUser = Depends(get_current_user)):
    return _matrix()


@router.put("/permissions/matrix")
def save_permission_matrix(_user: MrpUser = Depends(get_current_user)):
    return _matrix()


@router.get("/notifications/unread-count")
def unread_count(_user: MrpUser = Depends(get_current_user)):
    return {"unread_count": 0}


@router.get("/notifications")
def list_notifications(_user: MrpUser = Depends(get_current_user)):
    return []


@router.post("/notifications/{notification_id}/read")
def mark_read(notification_id: int, _user: MrpUser = Depends(get_current_user)):
    return {"status": "ok", "id": notification_id}


@router.post("/notifications/read-all")
def mark_all(_user: MrpUser = Depends(get_current_user)):
    return {"status": "ok"}
