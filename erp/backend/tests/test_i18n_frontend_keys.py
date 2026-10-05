"""Pastikan kunci i18n yang dipakai halaman admin ada di id/en/zh."""

from pathlib import Path

_I18N = Path(__file__).resolve().parents[2] / "frontend" / "src" / "i18n" / "index.js"


def test_common_saved_and_destination_present():
    text = _I18N.read_text(encoding="utf-8")
    assert "saved: 'Berhasil disimpan'" in text
    assert "saved: 'Saved successfully'" in text
    assert "saved: '保存成功'" in text
    assert "destination: 'Tujuan'" in text
    assert "destination: 'Destination'" in text
    assert "destination: '目的地'" in text


def test_en_invoice_payment_labels_present():
    text = _I18N.read_text(encoding="utf-8")
    assert "paymentDate: 'Transfer date'" in text
    assert "paymentBankAccount: 'Bank account'" in text
    assert "unpaid: 'Unpaid'" in text
