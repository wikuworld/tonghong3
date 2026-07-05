"""Unit tests for Pydantic schema validation."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import (
    CustomerCreate,
    PoDetailCreate,
)


class TestPoDetailCreate:
    def test_podetail_create_rejects_invalid_quantity(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(quantity_order=Decimal("-5"))
        errors = exc_info.value.errors()
        assert any("quantity_order must be greater than 0" in str(e) for e in errors)

    def test_podetail_create_accepts_zero_quantity(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(quantity_order=Decimal("0"))
        errors = exc_info.value.errors()
        assert any("quantity_order must be greater than 0" in str(e) for e in errors)

    def test_podetail_create_accepts_positive_quantity(self):
        detail = PoDetailCreate(quantity_order=Decimal("100"))
        assert detail.quantity_order == Decimal("100")

    def test_podetail_create_accepts_zero_price(self):
        detail = PoDetailCreate(unit_price=Decimal("0"))
        assert detail.unit_price == Decimal("0")

    def test_podetail_create_accepts_positive_price(self):
        detail = PoDetailCreate(unit_price=Decimal("15.50"))
        assert detail.unit_price == Decimal("15.50")

    def test_podetail_create_rejects_negative_price(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(unit_price=Decimal("-1"))
        errors = exc_info.value.errors()
        assert any(
            "unit_price must be greater than or equal to 0" in str(e)
            for e in errors
        )


class TestCustomerSchema:
    def test_customer_create_has_position_field(self):
        customer = CustomerCreate(
            code="C001",
            name="Test Customer",
            position="Manager",
            contact_person="John Doe",
        )
        assert customer.position == "Manager"

    def test_customer_create_position_optional(self):
        customer = CustomerCreate(code="C001", name="Test Customer")
        assert customer.position is None

    def test_customer_out_has_position_field(self):
        customer = CustomerCreate(position="Director")
        out_dict = customer.model_dump()
        assert "position" in out_dict
        assert out_dict["position"] == "Director"

    def test_customer_create_validates_export_flag(self):
        customer = CustomerCreate(
            code="C001",
            name="Export Customer",
            is_export_customer=True,
        )
        assert customer.is_export_customer is True

    def test_customer_create_accepts_multiple_contacts(self):
        customer = CustomerCreate(
            code="C001",
            name="Test Customer",
            contacts=[
                {"name": "Andi", "title": "Purchasing", "phone": "08123"},
                {"name": "Budi", "title": "Finance", "phone": "08124"},
            ],
        )
        assert len(customer.contacts) == 2
        assert customer.contacts[0].name == "Andi"

    def test_customer_create_accepts_main_and_billing_address(self):
        customer = CustomerCreate(
            code="C001",
            name="Test Customer",
            address="Jl. Utama No. 1",
            billing_address="Jl. Penagihan No. 2",
        )
        assert customer.address == "Jl. Utama No. 1"
        assert customer.billing_address == "Jl. Penagihan No. 2"


class TestColorFamilyValidation:
    def test_color_family_accepts_black(self):
        detail = PoDetailCreate(color_family="black")
        assert detail.color_family == "black"

    def test_color_family_accepts_color(self):
        detail = PoDetailCreate(color_family="color")
        assert detail.color_family == "color"

    def test_color_family_accepts_fluorescent(self):
        detail = PoDetailCreate(color_family="fluorescent")
        assert detail.color_family == "fluorescent"

    def test_color_family_rejects_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            PoDetailCreate(color_family="invalid")
        errors = exc_info.value.errors()
        assert any("color_family tidak valid" in str(e) for e in errors)
