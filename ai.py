import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY tidak ditemukan di file .env")


client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(timeout=60000),
)

MODEL_NAME = "gemini-3.5-flash-lite"


GAYA = """
Gunakan bahasa Indonesia yang jelas, sederhana, dan cocok untuk pelajar.

Jangan menggunakan salam pembuka.
Jangan menyebut AI, kecerdasan buatan, asisten AI, atau nama aplikasi.
Langsung masuk ke inti.
Gunakan paragraf pendek.
Berikan jarak antar paragraf.
Gunakan judul dan poin jika membantu.
Jangan membuat informasi yang tidak berhubungan dengan materi.
"""


def ambil_teks(response):
    teks = getattr(response, "text", None)
    return teks.strip() if teks else ""


def bersihkan_json(teks):
    teks = teks.strip()

    if teks.startswith("```json"):
        teks = teks[7:]
    elif teks.startswith("```JSON"):
        teks = teks[7:]
    elif teks.startswith("```"):
        teks = teks[3:]

    if teks.endswith("```"):
        teks = teks[:-3]

    return teks.strip()


def panggil_json(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    teks = ambil_teks(response)

    if not teks:
        raise RuntimeError("Model tidak mengembalikan data.")

    try:
        return json.loads(bersihkan_json(teks))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"JSON dari model tidak valid: {error}")


def jelaskan_materi(materi):
    prompt = f"""
Jelaskan materi berikut agar pelajar benar-benar mudah memahaminya.

{GAYA}

Struktur:
1. Pengertian
2. Konsep utama
3. Cara kerja atau proses jika ada
4. Hubungan antar konsep
5. Contoh
6. Hal penting yang harus diingat

Gunakan paragraf pendek dan beri satu baris kosong antar paragraf.

Jangan membuat soal.

MATERI:
{materi}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    teks = ambil_teks(response)

    if not teks:
        raise RuntimeError("Model tidak mengembalikan penjelasan.")

    return teks


def tanya_materi(materi, pertanyaan):
    prompt = f"""
Jawab pertanyaan berdasarkan materi berikut.

{GAYA}

Jawab langsung dan jelas.
Jika pertanyaan tidak dapat dijawab dari materi,
katakan bahwa informasi tersebut tidak tersedia
di materi yang diberikan.

MATERI:
{materi}

PERTANYAAN:
{pertanyaan}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    teks = ambil_teks(response)

    if not teks:
        raise RuntimeError("Model tidak mengembalikan jawaban.")

    return teks


def buat_paket_belajar(materi):
    prompt = f"""
Buat paket latihan ujian berdasarkan materi berikut.

{GAYA}

Buat tepat 5 soal pilihan ganda.

Setiap soal wajib memiliki:
- pertanyaan
- 4 pilihan A, B, C, D
- jawaban benar berupa A/B/C/D
- penjelasan jawaban

Semua soal WAJIB berdasarkan materi.
Jangan mengambil fakta dari luar materi.

Kembalikan HANYA JSON valid dengan format:

{{
    "ringkasan": "Ringkasan materi",
    "poin_penting": [
        "Poin 1",
        "Poin 2",
        "Poin 3"
    ],
    "soal": [
        {{
            "pertanyaan": "Pertanyaan",
            "pilihan": [
                "A. Jawaban A",
                "B. Jawaban B",
                "C. Jawaban C",
                "D. Jawaban D"
            ],
            "jawaban": "A",
            "penjelasan": "Penjelasan"
        }}
    ]
}}

MATERI:
{materi}
"""

    return panggil_json(prompt)


def buat_data_game(materi):
    prompt = f"""
Buat data game edukasi berdasarkan MATERI berikut.

Semua data HARUS berasal dari materi.
Jangan menggunakan fakta dari luar materi.

{GAYA}

MAZE:
Buat tepat 5 soal pilihan ganda untuk membuka 5 pintu.
Setiap soal memiliki pertanyaan, 4 pilihan A-D,
jawaban benar A/B/C/D, dan penjelasan.

MEMORY:
Buat tepat 6 pasangan.
Setiap pasangan memiliki "kata" dan "pasangan".
Keduanya harus berhubungan jelas berdasarkan materi.

PUZZLE:
Buat tepat 3 kalimat pendek yang berisi informasi penting.
Kalimat harus cukup pendek untuk layar HP.
Jangan gunakan tanda baca yang aneh.

Format WAJIB:

{{
    "maze": [
        {{
            "pertanyaan": "...",
            "pilihan": [
                "A. ...",
                "B. ...",
                "C. ...",
                "D. ..."
            ],
            "jawaban": "A",
            "penjelasan": "..."
        }}
    ],
    "memory": [
        {{
            "kata": "...",
            "pasangan": "..."
        }}
    ],
    "puzzle": [
        {{
            "kalimat": "..."
        }}
    ]
}}

Jangan tambahkan teks lain di luar JSON.

MATERI:
{materi}
"""

    data = panggil_json(prompt)

    if not isinstance(data.get("maze"), list):
        raise RuntimeError("Data maze tidak tersedia.")
    if not isinstance(data.get("memory"), list):
        raise RuntimeError("Data memory tidak tersedia.")
    if not isinstance(data.get("puzzle"), list):
        raise RuntimeError("Data puzzle tidak tersedia.")

    return data
