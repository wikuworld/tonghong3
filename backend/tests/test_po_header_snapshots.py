"""Unit tests for PO header snapshot helpers."""

from types import SimpleNamespace

from app.models import Brand, Customer
from app.services.po_header_snapshots import apply_header_snapshots, resolve_header_snapshots_for_list


class _FakeSession:
    def __init__(self, entities):
        self._entities = entities

    def get(self, model, pk):
        return self._entities.get((model, pk))


def test_apply_header_snapshots_fills_brand_and_customer():
    db = _FakeSession(
        {
            (Brand, 1): SimpleNamespace(id=1, name="NIKE", code="NIKE"),
            (Customer, 2): SimpleNamespace(id=2, name="PT Example", code="EX001"),
        }
    )
    data = {"brand_id": 1, "customer_id": 2}
    apply_header_snapshots(db, data, force=True)
    assert data["brand_name_snapshot"] == "NIKE"
    assert data["customer_name_snapshot"] == "PT Example"
    assert data["customer_code"] == "EX001"


def test_resolve_header_snapshots_for_list_without_db_write():
    brand = SimpleNamespace(id=1, name="NIKE", code="NIKE")
    po = SimpleNamespace(
        brand_id=1,
        brand_name_snapshot=None,
        customer_id=None,
        customer_name_snapshot=None,
        customer_code=None,
    )

    class _ListSession(_FakeSession):
        def scalars(self, _stmt):
            return SimpleNamespace(all=lambda: [brand])

    db = _ListSession({(Brand, 1): brand})
    resolve_header_snapshots_for_list(db, [po])
    assert po.brand_name_snapshot == "NIKE"
