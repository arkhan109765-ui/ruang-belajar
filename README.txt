RUANG BELAJAR - FILE BARU

File utama:
frontend/index.html
frontend/css/style.css
backend/main.py
backend/ai.py

Cara memakai:
1. Salin file-file ini ke project belajar-ai.
2. Pastikan .env tetap berisi GEMINI_API_KEY milikmu.
3. Aktifkan .venv.
4. Jalankan:
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
5. Buka:
   http://127.0.0.1:8000

Tidak perlu game.html, maze.html, memory.html, atau puzzle.html.
Semua tampilan berada di index.html dan backend menyediakan API.
