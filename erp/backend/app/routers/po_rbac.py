"""Dokumentasi RBAC endpoint PO — selaras dengan frontend ACTION_MATRIX (module `po`).

| Endpoint | Method | Roles |
|----------|--------|-------|
| /po, /po/page, /po/{id}, /po/{id}/details | GET | authenticated (view) |
| /po/next-number, /po/check-customer-ref, /po/material-hints | GET | authenticated |
| /po/mkt-workflow-stages | GET | authenticated |
| /po | POST | admin, marketing, sales |
| /po/{id}/duplicate | POST | admin, marketing, sales |
| /po/{id}/details | POST | admin, marketing, sales |
| /po/generate-lot, /po-detail/{id}/generate-lot | POST | admin, marketing, sales |
| /po/{id} | PUT | admin, marketing, sales, ppic |
| /po/{id}/marketing-revise | PATCH | admin, marketing |
| /po-detail/{id} | PUT | admin, marketing, ppic, finance |
| /po-detail/{id}/delivery-schedules | PUT | admin, marketing |
| /po/{id}/mkt-workflow/advance\|rollback | POST | admin, marketing, ppic |
| /po/{id} | DELETE | admin |
| /po-detail/{id} | DELETE | admin |

Frontend permissions.js (module po):
- view: admin, marketing, ppic, sales, production, finance
- create: admin, marketing, sales
- update: admin, marketing, sales, ppic, finance
- delete: admin
- advance: admin, marketing, ppic
"""
