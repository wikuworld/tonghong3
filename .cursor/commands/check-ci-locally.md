# Check CI locally (frontend + backend + docker smoke test)

Jalankan dari root project Tonghong:

1. Frontend quality gates:
   - `cd frontend`
   - `npm ci`
   - `npm run lint`
   - `npm run build`
   - `cd ..`
2. Backend quality gates:
   - `cd backend`
   - `pip install -r requirements.txt`
   - `python -m ruff check --select F,E9 app tests`
   - `python -m pytest`
   - `cd ..`
3. Optional smoke test container runtime (sesuai CI):
   - `docker compose build web backend`
   - `docker compose up -d mariadb backend web`
   - verifikasi `http://localhost:8000/health` mengembalikan status ok
   - verifikasi `http://localhost:8080` dapat diakses
   - `docker compose down -v`

Jika tool belum tersedia (mis. `npm`/`docker`), jelaskan perintah yang harus dijalankan user di mesinnya dan lanjutkan verifikasi yang bisa dilakukan.
