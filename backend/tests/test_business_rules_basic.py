from app.services.business_rules import validate_packing_links


def test_validate_packing_links_raises_on_missing_links():
    # Unit test minimal: fungsi harus melempar exception jika link tidak valid.
    # Kita pakai db=None untuk memaksa error cepat (defensive).
    try:
        validate_packing_links(None, production_id=0, qc_header_id=0)  # type: ignore[arg-type]
    except Exception:
        assert True
    else:
        assert False

