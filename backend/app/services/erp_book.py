"""ERP Production/QC/Packing adalah buku baca-saja; shopfloor hanya di MRP."""

from fastapi import HTTPException

SHOPFLOOR_WRITE_BLOCKED = (
    "Operasi shopfloor hanya di MRP. Halaman Production/QC/Packing adalah buku baca-saja."
)


def reject_erp_shopfloor_write() -> None:
    raise HTTPException(status_code=403, detail=SHOPFLOOR_WRITE_BLOCKED)
