"""Unit: paginated master items list."""

from unittest.mock import MagicMock

from app.routers.masters import _apply_master_item_list_filters, _master_item_stats
from app.models import MasterItem


def test_master_item_stats_counts_categories():
    db = MagicMock()
    db.execute.return_value.all.return_value = [
        ("PU", 10),
        ("Suede", 3),
        ("SubKon", 5),
    ]
    stats = _master_item_stats(db)
    assert stats.total == 18
    assert stats.pu == 10
    assert stats.suide == 3
    assert stats.subkon == 5


def test_apply_master_item_list_filters_keyword():
    from sqlalchemy import select

    stmt = _apply_master_item_list_filters(select(MasterItem), keyword="FG00001", category=None)
    compiled = str(stmt).lower()
    assert "master_items" in compiled
    assert "like" in compiled
