# Rebuild image frontend (Docker)

Jalankan di root project Tonghong (folder yang berisi `docker-compose.yml`):

1. `docker compose build web` atau `docker compose up -d --build web`
2. Pastikan service **`web`** jalan dan port **8080** memetakan ke **80** di container.
3. Jelaskan singkat: perubahan di `frontend/src` tidak masuk ke container production sampai image di-build ulang; untuk HMR pakai **`docker compose --profile dev up frontend-dev`** di port **5173**.

Jika `docker` tidak tersedia di lingkungan ini, jelaskan perintah yang harus dijalankan user di mesinnya.
