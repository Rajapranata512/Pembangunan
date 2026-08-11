# Platform Analisis Prospek Wilayah Jawa

Aplikasi web full-stack untuk membandingkan prospek usaha dan investasi properti pada 119 kabupaten/kota di enam provinsi Pulau Jawa. Platform menggabungkan data wilayah, mesin scoring, peta interaktif, rekomendasi berbasis tujuan, serta insight AI opsional.

## Fitur utama

- Dashboard peringkat dan ringkasan indikator wilayah.
- Peta interaktif berbasis Leaflet.
- Detail wilayah dan perbandingan beberapa wilayah.
- Skor potensi usaha, properti, pertumbuhan, risiko, dan skor akhir.
- Rekomendasi wilayah berdasarkan tujuan investasi.
- Chatbot, pembuatan insight, analisis sentimen, dan laporan PDF dengan Gemini; tersedia fallback bila API key belum diatur.
- Endpoint sinkronisasi sumber data eksternal.

## Teknologi

| Bagian | Teknologi |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, React Router, Recharts, Leaflet |
| Backend | FastAPI, Pydantic, SQLAlchemy |
| Database | SQLite untuk MVP lokal |
| AI | Google Gemini melalui `google-genai` |
| Laporan | ReportLab |

## Struktur proyek

```text
.
├── backend/            # API, model data, scoring, AI, dan data awal wilayah
│   ├── data/           # Dataset awal enam provinsi
│   └── routers/        # Endpoint FastAPI per domain
├── frontend/           # Aplikasi React + TypeScript
│   └── src/
│       ├── components/ # Komponen antarmuka bersama
│       └── pages/      # Enam halaman utama
├── PRD_Terstruktur/    # Kebutuhan bisnis, produk, data, dan arsitektur
└── ROADMAP.md          # Status MVP dan rencana pengembangan
```

## Menjalankan aplikasi

### 1. Backend

Gunakan Python 3.10 atau lebih baru.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn main:app --reload --port 8888
```

Saat startup, backend membuat database SQLite, mengisi data awal, dan menghitung skor wilayah. API tersedia di `http://localhost:8888` dan dokumentasi Swagger di `http://localhost:8888/docs`.

Gemini bersifat opsional. Isi `GEMINI_API_KEY` pada `backend/.env` untuk mengaktifkan fitur AI sebenarnya. Jangan commit file `.env`.

### 2. Frontend

Buka terminal kedua:

```powershell
cd frontend
npm install
npm run dev
```

Frontend tersedia di `http://localhost:3000`. Vite meneruskan request `/api` ke backend pada port `8888`.

## Validasi

Build frontend:

```powershell
cd frontend
npm run build
```

Dengan backend yang sedang berjalan, verifikasi endpoint utama:

```powershell
cd backend
python test_api.py
```

## Catatan penggunaan data

Proyek ini masih berstatus MVP. Data dan hasil scoring perlu diverifikasi kembali terhadap sumber resmi terbaru sebelum dipakai untuk keputusan investasi. Lihat [ROADMAP.md](ROADMAP.md) untuk keterbatasan saat ini dan rencana pengembangan.

