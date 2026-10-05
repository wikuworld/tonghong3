"""Unit tests for pricing engine validators and price resolution."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import PoDetailCreate
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer


class TestQuantityValidator:
    def test_quantity_validator_rejects_zero(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(quantity_order=Decimal("0"))
        assert "quantity_order must be greater than 0" in str(exc_info.value)

    def test_quantity_validator_rejects_negative(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(quantity_order=Decimal("-10"))
        assert "quantity_order must be greater than 0" in str(exc_info.value)

    def test_quantity_validator_accepts_positive(self):
        detail = PoDetailCreate(quantity_order=Decimal("100"))
        assert detail.quantity_order == Decimal("100")

    def test_quantity_validator_accepts_none(self):
        detail = PoDetailCreate(quantity_order=None)
        assert detail.quantity_order is None


class TestUnitPriceValidator:
    def test_unit_price_validator_rejects_negative(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(unit_price=Decimal("-5"))
        assert "unit_price must be greater than or equal to 0" in str(exc_info.value)

    def test_unit_price_validator_accepts_zero(self):
        detail = PoDetailCreate(unit_price=Decimal("0"))
        assert detail.unit_price == Decimal("0")

    def test_unit_price_validator_accepts_positive(self):
        detail = PoDetailCreate(unit_price=Decimal("12.50"))
        assert detail.unit_price == Decimal("12.50")

    def test_unit_price_validator_accepts_none(self):
        detail = PoDetailCreate(unit_price=None)
        assert detail.unit_price is None


class TestBuyerPriceResolution:
    def test_buyer_code_required_for_price_resolution(self, db_session):
        result = resolve_unit_price_for_buyer(db_session, buyer_code="")
        assert result["matched"] is False
        assert result["unit_price"] is None
        assert "buyer_code wajib diisi" in result["detail"]

    def test_buyer_code_none_returns_error(self, db_session):
        result = resolve_unit_price_for_buyer(db_session, buyer_code=None)
        assert result["matched"] is False
        assert "buyer_code wajib diisi" in result["detail"]
