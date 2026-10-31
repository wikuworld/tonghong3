"""Parser workbook resmi + resolve addon Color / blok Nike."""

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.buyer_price_aliases import (
    canonical_customer_code,
    customer_price_rules,
    emboss_is_special,
    infer_price_block,
    is_outside_banten_factory,
    list_price_rules,
    normalize_material_alias,
)
from app.services.buyer_price_import import (
    STANDARD_COLUMN_KEYS,
    build_price_cells,
    parse_adidas_quotation_xlsx,
    parse_nike_tempel_xlsx,
)
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer

DOC = Path("/app/dokumentasi")
if not DOC.is_dir():
    DOC = Path(__file__).resolve().parents[2] / "dokumentasi"


def _adidas_path() -> Path | None:
    for name in (
        "1._QUOTATION_ADIDAS_FW26_FEB-JUL_2026_ (1).xlsx",
        "1._QUOTATION_ADIDAS_FW26_FEB-JUL_2026_ (2).xlsx",
    ):
        p = DOC / name
        if p.is_file():
            return p
    return None


def _nike_path() -> Path | None:
    for name in (
        "HARGA_TEMPEL_NIKE_JUL_-_DES_2026_UPDATE (1).xlsx",
        "HARGA_TEMPEL_NIKE_JUL_-_DES_2026_UPDATE (2).xlsx",
    ):
        p = DOC / name
        if p.is_file():
            return p
    return None


def test_build_price_cells_color_addon():
    row = build_price_cells(
        item="PU COATED LEATHER (MAP-ACTION LEATHER)",
        thickness="1.2-1.6",
        white=1.12,
        black=1.15,
        color=1.18,
        fluo=1.28,
        metallic=0.10,
        metallic_is_addon=True,
    )
    assert row["COLOR WHITE"] == "1.12"
    assert row["COLOR BLACK"] == "0.03"
    assert row["COLOR COLOR"] == "0.06"
    assert row["FLOURASENT"] == "0.16"
    assert row["METALIC"] == "0.1"


def test_aliases_and_blocks():
    assert normalize_material_alias("'LACCATTO PATENT LEATHER - EPM 5") == "LACCATO PATENT LEATHER"
    assert normalize_material_alias("METAL LEATHER - PATENT") == "METAL LEATHER-PATENT"
    assert canonical_customer_code("HW035") == "HW036"
    assert canonical_customer_code("HI-001") == "HA001"
    assert emboss_is_special("AR-140 DM")
    assert not emboss_is_special("")
    assert infer_price_block(emboss="AR-140", outside_banten=False) == "SPECIAL"
    assert infer_price_block(emboss="", outside_banten=True) == "OUTSIDE BANTEN"
    assert infer_price_block(emboss="AR-140", outside_banten=True) == "OUTSIDE SPECIAL"
    assert infer_price_block(emboss="", outside_banten=False) == "COMMON"


def test_parse_adidas_quotation_has_color_addon():
    path = _adidas_path()
    if path is None:
        return
    parsed = parse_adidas_quotation_xlsx(path)
    assert len(parsed["data_rows"]) == 17
    action = next(r for r in parsed["data_rows"] if r["ITEM"].startswith("PU COATED LEATHER (MAP-ACTION LEATHER)") and "AR-140" not in r["ITEM"])
    assert action["COLOR WHITE"] == "1.12"
    assert action["COLOR COLOR"] == "0.06"
    flat = next(r for r in parsed["data_rows"] if r["ITEM"] == "HYDRO ECO TECH COMFORT")
    assert flat["COLOR COLOR"] == "0"


def test_parse_nike_tempel_blocks():
    path = _nike_path()
    if path is None:
        return
    parsed = parse_nike_tempel_xlsx(path)
    blocks = {r["COLOR"] for r in parsed["data_rows"]}
    assert "COMMON" in blocks
    assert "SPECIAL" in blocks
    assert "OUTSIDE BANTEN" in blocks
    assert "OUTSIDE SPECIAL" in blocks
    generic = [
        r
        for r in parsed["data_rows"]
        if r["ITEM"] == "GENERIC PU COATED"
    ]
    common = next(r for r in generic if r["COLOR"] == "COMMON")
    assert common["COLOR WHITE"] == "1.13"
    assert common["COLOR COLOR"] == "0.1"
    laccato_os = next(
        r for r in parsed["data_rows"] if "LACCATO" in r["ITEM"].upper() and r["COLOR"] == "OUTSIDE SPECIAL"
    )
    assert float(laccato_os["COLOR WHITE"]) == 1.9
    assert len([r for r in parsed["data_rows"] if r["COLOR"] == "OUTSIDE SPECIAL"]) >= 20


def _mock_db_with_list(rows):
    db = MagicMock()
    lst = MagicMock()
    lst.id = 22
    lst.period_start = None
    lst.period_end = None
    db.scalars.return_value.all.return_value = [lst]

    def fake_list(_db, _id):
        return {"rows": rows, "meta_json": {"column_keys": STANDARD_COLUMN_KEYS}}

    return db, fake_list


def test_resolve_color_family_addon(monkeypatch):
    rows = [
        build_price_cells(
            item="(PM) GENERIC PU COATED",
            block="COMMON",
            white=1.08,
            black=1.13,
            color=1.18,
            fluo=1.23,
            metallic=1.28,
        ),
        build_price_cells(
            item="GENERIC PU COATED",
            block="COMMON",
            white=1.13,
            black=1.18,
            color=1.23,
            fluo=1.38,
            metallic=1.38,
        ),
        build_price_cells(
            item="GENERIC PU COATED AR-181 M 1.46",
            block="SPECIAL",
            white=1.13,
            black=1.18,
            color=1.23,
            fluo=1.38,
            metallic=1.38,
        ),
    ]
    db, fake = _mock_db_with_list(rows)
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", fake)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    r = resolve_unit_price_for_buyer(
        db, "NIKE", material_name="GENERIC PU COATED", color_family="color"
    )
    assert r["matched"] is True
    assert r["unit_price"] == Decimal("1.23")
    white = resolve_unit_price_for_buyer(db, "NIKE", material_name="GENERIC PU COATED", color_family=None)
    assert white["unit_price"] == Decimal("1.13")


def test_resolve_prefers_common_without_emboss(monkeypatch):
    rows = [
        build_price_cells(item="VIRGIN HYDRO PU", block="COMMON", white=1.13, black=1.18, color=1.23, fluo=1.38, metallic=1.38),
        build_price_cells(item="VIRGIN HYDRO PU", block="SPECIAL", white=1.23, black=1.28, color=1.33, fluo=1.48, metallic=1.48),
    ]
    db, fake = _mock_db_with_list(rows)
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", fake)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    r = resolve_unit_price_for_buyer(db, "NIKE", material_name="VIRGIN HYDRO PU", color_family="color")
    assert r["unit_price"] == Decimal("1.23")
    assert r["base_price"] == Decimal("1.13")
    assert r["addons"] == [{"key": "COLOR COLOR", "label": "+ COLOR", "amount": Decimal("0.10")}]


def test_resolve_special_emboss_and_outside(monkeypatch):
    rows = [
        build_price_cells(item="GENERIC PU COATED", block="COMMON", white=1.13, black=1.18, color=1.23, fluo=1.38, metallic=1.38),
        build_price_cells(item="GENERIC PU COATED", block="SPECIAL", white=1.23, black=1.28, color=1.33, fluo=1.48, metallic=1.48),
        build_price_cells(item="GENERIC PU COATED", block="OUTSIDE BANTEN", white=1.15, black=1.20, color=1.25, fluo=1.40, metallic=1.40),
        build_price_cells(item="GENERIC PU COATED", block="OUTSIDE SPECIAL", white=1.25, black=1.30, color=1.35, fluo=1.50, metallic=1.50),
    ]
    db, fake = _mock_db_with_list(rows)
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", fake)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    special = resolve_unit_price_for_buyer(
        db, "NIKE", material_name="GENERIC PU COATED", color_family="color", emboss="AR-140"
    )
    assert special["unit_price"] == Decimal("1.33")
    assert special["price_block"] == "SPECIAL"

    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: True)
    lst = db.scalars.return_value.all.return_value[0]
    lst.outside_price_adjust = Decimal("0.20")
    lst.outside_adjust_type = "nominal"
    lst.discount_modifier_enabled = True
    lst.discount_modifier = Decimal("0.05")
    lst.discount_modifier_type = "nominal"
    outside = resolve_unit_price_for_buyer(
        db, "NIKE", material_name="GENERIC PU COATED", color_family="color", factory_code="BI020"
    )
    assert outside["unit_price"] == Decimal("1.20")
    assert outside["price_block"] == "OUTSIDE BANTEN"
    assert not any(addon["key"] == "OUTSIDE ADJUST" for addon in outside["addons"])
    assert any(addon["key"] == "DISCOUNT MODIFIER" for addon in outside["addons"])


def test_resolve_laccato_alias(monkeypatch):
    rows = [
        build_price_cells(item="LACCATO PATENT LEATHER", block="SPECIAL", white=1.88, black=1.88, color=1.88, fluo=2.13, metallic=2.13),
    ]
    db, fake = _mock_db_with_list(rows)
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", fake)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    r = resolve_unit_price_for_buyer(
        db, "NIKE", material_name="'LACCATTO PATENT LEATHER - EPM 5", color_family="color", emboss="AR-140"
    )
    assert r["matched"] is True
    assert r["unit_price"] == Decimal("1.88")


def test_outside_banten_follows_customer_flag_only():
    customer = SimpleNamespace(
        code="XX001",
        outside_banten=False,
        wilayah_province_code="32",
        city="CIREBON",
        address="JAWA TENGAH",
        billing_address="",
    )
    db = MagicMock()
    db.scalars.return_value.first.return_value = customer
    assert is_outside_banten_factory(db, "XX001") is False
    customer.outside_banten = True
    assert is_outside_banten_factory(db, "BI020") is True
    assert infer_price_block(emboss="", outside_banten=True) == "OUTSIDE BANTEN"
    assert infer_price_block(emboss="", outside_banten=False) == "COMMON"


def test_list_price_rules_skip_zero_and_disabled_discount():
    price_list = SimpleNamespace(
        outside_price_adjust=Decimal("0.20"),
        outside_adjust_type="nominal",
        discount_modifier_enabled=False,
        discount_modifier=Decimal("0.05"),
        discount_modifier_type="percent",
    )
    rules = list_price_rules(price_list)
    assert rules["outside"] == {"type": "nominal", "value": Decimal("0.20")}
    assert rules["discount"] is None
    price_list.discount_modifier_enabled = True
    rules = list_price_rules(price_list)
    assert rules["discount"] == {"type": "percent", "value": Decimal("0.05")}
    price_list.outside_price_adjust = Decimal("0")
    assert list_price_rules(price_list)["outside"] is None


def test_resolve_header_adjust_only_without_outside_block(monkeypatch):
    rows = [
        build_price_cells(
            item="GENERIC PU COATED",
            block="COMMON",
            white=1.13,
            black=1.18,
            color=1.23,
            fluo=1.40,
            metallic=1.40,
        ),
    ]
    db, fake = _mock_db_with_list(rows)
    lst = db.scalars.return_value.all.return_value[0]
    lst.outside_price_adjust = Decimal("0.20")
    lst.outside_adjust_type = "nominal"
    lst.discount_modifier_enabled = False
    lst.discount_modifier = Decimal("0.05")
    lst.discount_modifier_type = "nominal"
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", fake)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    inside = resolve_unit_price_for_buyer(db, "ADIDAS", material_name="GENERIC PU COATED", color_family="color")
    unit = inside["unit_price"]
    assert not any(addon["key"] == "OUTSIDE ADJUST" for addon in inside["addons"])

    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: True)
    bumped = resolve_unit_price_for_buyer(db, "ADIDAS", material_name="GENERIC PU COATED", color_family="color")
    assert bumped["unit_price"] == unit + Decimal("0.20")

    lst.outside_adjust_type = "percent"
    lst.outside_price_adjust = Decimal("10")
    lst.discount_modifier_enabled = True
    mixed = resolve_unit_price_for_buyer(db, "ADIDAS", material_name="GENERIC PU COATED", color_family="color")
    after_outside = (unit + (unit * Decimal("10") / Decimal(100)).quantize(Decimal("0.0001"))).quantize(Decimal("0.0001"))
    assert mixed["unit_price"] == (after_outside - Decimal("0.05")).quantize(Decimal("0.0001"))
    assert any(addon["key"] == "OUTSIDE ADJUST" for addon in mixed["addons"])
    assert any(addon["key"] == "DISCOUNT MODIFIER" and addon["amount"] < 0 for addon in mixed["addons"])

    lst.outside_price_adjust = None
    lst.discount_modifier_enabled = False
    plain = resolve_unit_price_for_buyer(db, "ADIDAS", material_name="GENERIC PU COATED", color_family="color")
    assert plain["unit_price"] == unit


def test_customer_price_rules_reads_enabled_discount():
    customer = SimpleNamespace(
        code="BI020",
        discount_modifier_enabled=True,
        discount_modifier=Decimal("0.05"),
        discount_modifier_type="nominal",
    )
    db = MagicMock()
    db.scalars.return_value.first.return_value = customer
    rules = customer_price_rules(db, "BI020")
    assert rules["outside"] is None
    assert rules["discount"] == {"type": "nominal", "value": Decimal("0.05")}
    customer.discount_modifier_enabled = False
    assert customer_price_rules(db, "BI020")["discount"] is None
    customer.discount_modifier_enabled = True
    customer.discount_modifier = Decimal("0")
    assert customer_price_rules(db, "BI020")["discount"] is None


def test_factory_discount_applies_only_to_that_factory(monkeypatch):
    rows = [
        build_price_cells(
            item="GENERIC PU COATED",
            block="COMMON",
            white=1.00,
            color=1.10,
        ),
    ]
    db, fake = _mock_db_with_list(rows)
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", fake)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)

    def rules(_db, factory_code):
        if factory_code == "BI020":
            return {"outside": None, "discount": {"type": "nominal", "value": Decimal("0.05")}}
        return {"outside": None, "discount": None}

    monkeypatch.setattr("app.services.buyer_price_resolve.customer_price_rules", rules)
    discounted = resolve_unit_price_for_buyer(
        db,
        "NIKE",
        material_name="GENERIC PU COATED",
        color_family="color",
        factory_code="BI020",
    )
    other = resolve_unit_price_for_buyer(
        db,
        "NIKE",
        material_name="GENERIC PU COATED",
        color_family="color",
        factory_code="CS004",
    )
    assert discounted["unit_price"] == Decimal("1.05")
    assert any(addon["key"] == "FACTORY DISCOUNT" for addon in discounted["addons"])
    assert other["unit_price"] == Decimal("1.10")
    assert not any(addon["key"] == "FACTORY DISCOUNT" for addon in other["addons"])
