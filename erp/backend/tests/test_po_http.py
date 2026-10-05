"""HTTP integration tests for PO router guards and basic handler paths."""

from types import SimpleNamespace

from app.models import PoDetail, PoHeader, ProductionOrder

from tests.http_fixtures import (
    DummyDbSession,
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


class _PoDeleteDb(DummyDbSession):
  def __init__(self, *, po, production=None, block_reason=None):
    super().__init__()
    self.po = po
    self.production = production
    self.block_reason = block_reason
    self.deleted = False

  def get(self, model, obj_id):
    if model is PoHeader and obj_id == getattr(self.po, "id", None):
      return self.po
    if model is ProductionOrder and self.production and obj_id == self.production.id:
      return self.production
    return None

  def query(self, model):
    class _Q:
      def __init__(self, outer, model):
        self.outer = outer
        self.model = model

      def filter(self, *args, **kwargs):
        return self

      def count(self):
        if self.outer.block_reason == "subcon":
          return 1
        if self.outer.block_reason == "ppic":
          return 1
        return 0

    return _Q(self, model)

  def scalars(self, _stmt):
    class _R:
      def __init__(self, outer):
        self.outer = outer

      def first(self):
        if self.outer.block_reason == "production":
          return 99
        if self.outer.block_reason == "invoice":
          return 1
        if self.outer.block_reason == "delivery":
          return 1
        return None

      def all(self):
        return []

    return _R(self)

  def delete(self, obj):
    self.deleted = True

  def add(self, _obj):
    return None

  def commit(self):
    return None


class _PoConfirmDb(DummyDbSession):
  def __init__(self, *, po, detail_count=0, missing_lot_ids=None):
    super().__init__()
    self.po = po
    self.detail_count = detail_count
    self.missing_lot_ids = list(missing_lot_ids or [])

  def get(self, model, obj_id):
    if model is PoHeader:
      return self.po
    return None

  def scalar(self, _stmt):
    return self.detail_count

  def scalars(self, _stmt):
    outer = self

    class _R:
      def all(self):
        return list(outer.missing_lot_ids)

      def first(self):
        return outer.missing_lot_ids[0] if outer.missing_lot_ids else None

    return _R()

  def commit(self):
    return None

  def refresh(self, _row):
    return None


def test_po_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/po", 401)
    finally:
        clear_api_overrides()


def test_po_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(
            client,
            "POST",
            f"{_PREFIX}/po",
            403,
            {"po_category": "production", "customer_id": 1},
        )
    finally:
        clear_api_overrides()


def test_po_get_missing_returns_404():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "GET", f"{_PREFIX}/po/999", 404)
    finally:
        clear_api_overrides()


def test_po_delete_non_admin_forbidden():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "DELETE", f"{_PREFIX}/po/1", 403)
    finally:
        clear_api_overrides()


def test_po_delete_blocked_when_production_exists():
    po = SimpleNamespace(id=7, po_number="SO-TEST", status="draft")
    client = make_api_client(_PoDeleteDb(po=po, block_reason="production"))
    set_auth_user("admin")
    try:
        resp = client.delete(f"{_PREFIX}/po/7")
        assert resp.status_code == 400
        assert "production" in resp.json()["detail"].lower()
    finally:
        clear_api_overrides()


def test_po_delete_allowed_for_clean_draft():
    po = SimpleNamespace(id=8, po_number="SO-DRAFT", status="draft")
    db = _PoDeleteDb(po=po)
    client = make_api_client(db)
    set_auth_user("admin")
    try:
        resp = client.delete(f"{_PREFIX}/po/8")
        assert resp.status_code == 200
        assert db.deleted is True
    finally:
        clear_api_overrides()


def test_po_confirm_without_details_rejected():
    po = SimpleNamespace(
        id=9,
        po_number="SO-EMPTY",
        status="draft",
        customer_id=None,
        brand_id=None,
        buyer="NB",
        po_customer_ref="REF-9",
        mkt_workflow_stage="input_system",
    )
    client = make_api_client(_PoConfirmDb(po=po, detail_count=0))
    set_auth_user("marketing")
    try:
        resp = client.put(f"{_PREFIX}/po/9", json={"status": "confirmed"})
        assert resp.status_code == 400
        assert "baris detail" in resp.json()["detail"].lower()
    finally:
        clear_api_overrides()


def test_po_confirm_without_lot_rejected():
    po = SimpleNamespace(
        id=10,
        po_number="SO-NO-LOT",
        status="draft",
        customer_id=None,
        brand_id=None,
        buyer="NB",
        po_customer_ref="REF-10",
        mkt_workflow_stage="input_system",
    )
    client = make_api_client(_PoConfirmDb(po=po, detail_count=2, missing_lot_ids=[101, 102]))
    set_auth_user("marketing")
    try:
        resp = client.put(f"{_PREFIX}/po/10", json={"status": "confirmed"})
        assert resp.status_code == 400
        detail = resp.json()["detail"].lower()
        assert "no lot" in detail or "lot" in detail
    finally:
        clear_api_overrides()


def test_po_workflow_advance_wrong_role():
    client = make_api_client()
    set_auth_user("warehouse")
    try:
        assert_status(client, "POST", f"{_PREFIX}/po/1/mkt-workflow/advance", 403)
    finally:
        clear_api_overrides()


def test_po_mkt_workflow_stages_ok():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        resp = client.get(f"{_PREFIX}/po/mkt-workflow-stages")
        assert resp.status_code == 200
        body = resp.json()
        assert "stages" in body
        assert isinstance(body["stages"], list)
        assert len(body["stages"]) >= 1
    finally:
        clear_api_overrides()


def test_po_delivery_schedules_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/po-detail/1/delivery-schedules", 401)
    finally:
        clear_api_overrides()


def test_po_delivery_schedules_missing_detail_404():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "GET", f"{_PREFIX}/po-detail/999/delivery-schedules", 404)
    finally:
        clear_api_overrides()


def test_po_delivery_schedules_returns_rows():
    schedule = SimpleNamespace(id=1, po_detail_id=5, sequence_no=1, qty=10, delivery_date=None)
    detail = SimpleNamespace(delivery_schedules=[schedule])

    def _get(model, obj_id):
        if model is PoDetail and obj_id == 5:
            return detail
        return None

    client = make_api_client(DummyDbSession(get_handler=_get))
    set_auth_user("marketing")
    try:
        resp = client.get(f"{_PREFIX}/po-detail/5/delivery-schedules")
        assert resp.status_code == 200
        assert resp.json()[0]["sequence_no"] == 1
    finally:
        clear_api_overrides()

