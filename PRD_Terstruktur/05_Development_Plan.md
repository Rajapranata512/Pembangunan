# Bagian 5: Development Roadmap & Plan
**Proyek:** Platform Analisis Prospek Wilayah Jawa

## 18. Development Roadmap (Estimasi: 3-5 Bulan MVP)
1. **Fase 1 (W1-2):** Perencanaan PRD final, Wireframe, ERD, API Contract.
2. **Fase 2 (W2-4):** Pengumpulan dataset 119 kota/kabupaten.
3. **Fase 3 & 4 (W5-6):** Data Cleaning dan Skrip Scoring Engine (Python/Pandas).
4. **Fase 5 (W6-9):** Setup PostgreSQL & API Endpoint (FastAPI).
5. **Fase 6 (W9-12):** Frontend MVP (Dashboard, Region Detail, Peta Interaktif).
6. **Fase 7 (W12-13):** Integrasi AI Insight Claude API.
7. **Fase 8 & 9 (W14-17):** Comparison, Recommendation Engine, Testing E2E, Deploy ke Vercel & Railway.

## 21. Checklist Persiapan Development
- [ ] Wireframe & UI Design telah disetujui.
- [ ] Schema database (ERD) siap diimplementasi.
- [ ] Daftar & Bobot indikator skoring divalidasi oleh domain expert.
- [ ] Ketersediaan sumber data awal untuk 10 kota sampel sudah terkonfirmasi.
- [ ] API Contract antara Frontend dan Backend telah didokumentasikan.

## Prompt Lanjutan untuk AI Coding Agent
Apabila akan mendelegasikan ke AI Agent (e.g. Cursor / Github Copilot / Gemini), gunakan urutan ini:
1. **Untuk Backend:** Berikan bagian `04_Technical_Architecture.md` dan `03_Data_and_Scoring.md` untuk membuat model SQLAlchemy, script Pandas normalisasi, dan endpoint FastAPI.
2. **Untuk Frontend Dashboard:** Berikan bagian `02_Product_Features.md` dan `04_Technical_Architecture.md` (API endpoint) untuk membuat komponen Next.js dan fetching data.
3. **Untuk Peta:** Berikan bagian spesifik `Map Explorer` di bagian 2, untuk membangun komponen React-Leaflet membaca GeoJSON.
