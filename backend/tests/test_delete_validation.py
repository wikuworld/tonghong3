"""Unit tests for delete validations."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.routers.customers import delete_customer
from app.routers.buyer_prices import delete_buyer_price_list
from app.models import Customer, BuyerPriceList


class TestCustomerDeleteValidation:
    def test_delete_customer_with_no_related_pos(self, db_session):
        """Customer without POs should be deletable."""
        customer = MagicMock(spec=Customer)
        customer.id = 1
        db_session.get.return_value = customer
        db_session.query.return_value.filter.return_value.count.return_value = 0

        result = delete_customer(customer_id=1, db=db_session, _user=MagicMock())

        assert result == {"status": "deleted"}
        db_session.delete.assert_called_once_with(customer)
        db_session.commit.assert_called_once()

    def test_delete_customer_with_active_pos(self, db_session):
        """Customer with POs should NOT be deletable."""
        customer = MagicMock(spec=Customer)
        customer.id = 1
        db_session.get.return_value = customer
        db_session.query.return_value.filter.return_value.count.return_value = 3

        with pytest.raises(HTTPException) as exc_info:
            delete_customer(customer_id=1, db=db_session, _user=MagicMock())

        assert exc_info.value.status_code == 400
        assert "tidak bisa dihapus" in exc_info.value.detail
        assert "3" in exc_info.value.detail
        db_session.delete.assert_not_called()

    def test_delete_customer_not_found(self, db_session):
        """Deleting non-existent customer should raise 404."""
        db_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_customer(customer_id=999, db=db_session, _user=MagicMock())

        assert exc_info.value.status_code == 404
        assert "tidak ditemukan" in exc_info.value.detail


class TestBuyerPriceDeleteValidation:
    def test_delete_buyer_price_with_no_pos(self, db_session):
        """Buyer price without POs should be deletable."""
        buyer = MagicMock(spec=BuyerPriceList)
        buyer.id = 1
        buyer.buyer_code = "NB-TEST"
        db_session.get.return_value = buyer
        db_session.query.return_value.filter.return_value.count.return_value = 0

        result = delete_buyer_price_list(list_id=1, db=db_session, _user=MagicMock())

        assert result == {"status": "deleted"}
        db_session.delete.assert_called_once_with(buyer)
        db_session.commit.assert_called_once()

    def test_delete_buyer_price_with_pos(self, db_session):
        """Buyer price used in POs should NOT be deletable."""
        buyer = MagicMock(spec=BuyerPriceList)
        buyer.id = 1
        buyer.buyer_code = "ADIDAS-TEST"
        db_session.get.return_value = buyer
        db_session.query.return_value.filter.return_value.count.return_value = 2

        with pytest.raises(HTTPException) as exc_info:
            delete_buyer_price_list(list_id=1, db=db_session, _user=MagicMock())

        assert exc_info.value.status_code == 400
        assert "tidak bisa dihapus" in exc_info.value.detail
        assert "ADIDAS-TEST" in exc_info.value.detail
        assert "2" in exc_info.value.detail
        db_session.delete.assert_not_called()

    def test_delete_buyer_price_not_found(self, db_session):
        """Deleting non-existent buyer price should raise 404."""
        db_session.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_buyer_price_list(list_id=999, db=db_session, _user=MagicMock())

        assert exc_info.value.status_code == 404
        assert "tidak ditemukan" in exc_info.value.detail
