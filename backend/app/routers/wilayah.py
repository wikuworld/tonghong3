"""Proxy data wilayah administrasi Indonesia (sumber publik; diakses lewat backend agar tidak kena CORS browser)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import quote

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["wilayah"])

UA = "Tonghong-ERP/1.0"
BASE = "https://wilayah.id/api"
TIMEOUT = 25


def _code_path_segment(code: str) -> str:
    """Kode wilayah boleh mengandung titik; jaga agar aman di path URL."""
    return quote((code or "").strip(), safe=".")


def _fetch_json(path: str) -> dict:
    """path mis. /provinces.json atau /regencies/31.json"""
    url = f"{BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=e.code, detail=f"Layanan wilayah: {e.reason}") from e
    except urllib.error.URLError as e:
        raise HTTPException(status_code=502, detail=f"Tidak dapat mengambil data wilayah: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail="Respons data wilayah bukan JSON") from e


@router.get("/wilayah/provinces")
def wilayah_provinces() -> dict:
    return _fetch_json("/provinces.json")


@router.get("/wilayah/regencies/{province_code}")
def wilayah_regencies(province_code: str) -> dict:
    return _fetch_json(f"/regencies/{_code_path_segment(province_code)}.json")


@router.get("/wilayah/districts/{regency_code}")
def wilayah_districts(regency_code: str) -> dict:
    return _fetch_json(f"/districts/{_code_path_segment(regency_code)}.json")


@router.get("/wilayah/villages/{district_code}")
def wilayah_villages(district_code: str) -> dict:
    return _fetch_json(f"/villages/{_code_path_segment(district_code)}.json")
