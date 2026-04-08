from decimal import Decimal

from app.routers.marketing import BalanceFilter, _passes_balance_value


def test_balance_filter_all_accepts_anything():
    assert _passes_balance_value(None, BalanceFilter.all) is True
    assert _passes_balance_value(Decimal("0"), BalanceFilter.all) is True
    assert _passes_balance_value(Decimal("10"), BalanceFilter.all) is True


def test_balance_filter_exclude_zero():
    assert _passes_balance_value(None, BalanceFilter.exclude_zero) is True
    assert _passes_balance_value(Decimal("0"), BalanceFilter.exclude_zero) is False
    assert _passes_balance_value(Decimal("0.00"), BalanceFilter.exclude_zero) is False
    assert _passes_balance_value(Decimal("0.01"), BalanceFilter.exclude_zero) is True


def test_balance_filter_positive_only():
    assert _passes_balance_value(None, BalanceFilter.positive_only) is False
    assert _passes_balance_value(Decimal("-1"), BalanceFilter.positive_only) is False
    assert _passes_balance_value(Decimal("0"), BalanceFilter.positive_only) is False
    assert _passes_balance_value(Decimal("1"), BalanceFilter.positive_only) is True

