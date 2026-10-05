# MRP UAT

- API: `tonghong-uat-mrp-api` → `mrp/backend` port 8002
- UI: `tonghong-uat-mrp-ui` → `mrp/frontend` port 8082
- Identitas: `uat_tonghong_mrp.mrp_users`, JWT `iss=tonghong-mrp` `aud=mrp`

Handler shopfloor lama ada di `backend/legacy/` dan di-load in-process oleh FastAPI. Tidak ada unit Flask / port 5011.
