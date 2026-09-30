from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.ai import (
    jelaskan_materi,
    tanya_materi,
    buat_paket_belajar,
    buat_data_game,
)


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Ruang Belajar",
    version="3.0.0",
)

app.mount(
    "/css",
    StaticFiles(directory=FRONTEND_DIR / "css"),
    name="css",
)


@app.get("/")
async def halaman_utama():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/manifest.json")
async def manifest():
    path = FRONTEND_DIR / "manifest.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Manifest tidak tersedia.")
    return FileResponse(path, media_type="application/manifest+json")


@app.get("/api/status")
async def status():
    return {
        "status": "ok",
        "message": "Backend Ruang Belajar berhasil berjalan.",
    }


class MateriRequest(BaseModel):
    materi: str


class TanyaRequest(BaseModel):
    materi: str
    pertanyaan: str


def validasi_materi(materi: str):
    materi = materi.strip()
    if not materi:
        raise HTTPException(
            status_code=400,
            detail="Materi tidak boleh kosong.",
        )
    return materi


@app.post("/api/rangkuman")
async def rangkuman(request: MateriRequest):
    materi = validasi_materi(request.materi)
    try:
        return {"hasil": jelaskan_materi(materi)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/api/tanya")
async def tanya(request: TanyaRequest):
    materi = validasi_materi(request.materi)
    pertanyaan = request.pertanyaan.strip()

    if not pertanyaan:
        raise HTTPException(
            status_code=400,
            detail="Pertanyaan tidak boleh kosong.",
        )

    try:
        return {"hasil": tanya_materi(materi, pertanyaan)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/api/paket-belajar")
async def paket_belajar(request: MateriRequest):
    materi = validasi_materi(request.materi)

    try:
        return buat_paket_belajar(materi)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/api/data-game")
async def data_game(request: MateriRequest):
    materi = validasi_materi(request.materi)

    try:
        return buat_data_game(materi)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
