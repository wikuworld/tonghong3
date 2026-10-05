"""Roll/pieces MRP packing → outstanding ship options."""

from app.services.mrp_fg_packing_options import _fetch_mrp_packing_roll_pcs


def test_fetch_mrp_packing_roll_pcs_parses_rolls_and_lembar(monkeypatch):
    class FakeResp:
        status_code = 200
        content = b"{}"

        @staticmethod
        def json():
            return {
                "packing": {"total_lembar": 120, "kode_packing": "FG-1"},
                "rolls": [{"roll_no": 1, "lembar": 60}, {"roll_no": 2, "lembar": 60}],
            }

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            assert "/api/mrp/packing/99" in url
            return FakeResp()

    monkeypatch.setattr(
        "app.services.mrp_fg_packing_options.httpx.Client",
        lambda **kwargs: FakeClient(),
    )
    rolls, pieces = _fetch_mrp_packing_roll_pcs(99)
    assert rolls == 2
    assert pieces == 120
