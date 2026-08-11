# Bagian 1: Business Requirements & Scope
**Proyek:** Platform Analisis Prospek Wilayah Jawa

## 1. Executive Summary
Platform pendukung keputusan berbasis data untuk mencari lokasi terbaik di Pulau Jawa (119 kota/kabupaten). Mengintegrasikan data demografi, ekonomi, dan infrastruktur ke dalam skor, peta interaktif, dan rekomendasi AI.

## 2. Background
Pulau Jawa padat aktivitas ekonomi namun penentuan lokasi investasi sering berbasis insting/tren. Data tersebar dan sulit diakses cepat, sehingga investor kerap tertinggal menangkap peluang sebelum harga aset melonjak.

## 3. Problem Statement
- Belum ada sistem terpusat perbandingan antarwilayah.
- Data tersebar di puluhan sumber.
- Keputusan sering tidak berbasis data objektif.
- Keterlambatan menemukan daerah berkembang.

## 4. Product Vision
Menjadi platform referensi utama yang transparan dan berbasis data bagi investor/pengusaha dalam melihat prospek wilayah Pulau Jawa.

## 5. Goals and Objectives
- **Bisnis:** Menyediakan sistem data investasi; Menjadi referensi utama.
- **Produk:** Skor 119 kota/kabupaten; Dashboard & Peta Interaktif; Rekomendasi tujuan; AI insight.
- **Metrik Keberhasilan MVP:** 119 wilayah terskor; Load < 3s; Data > 80% terisi; Validasi skor logis.

## 6. Target Users
- **Investor Properti:** Mencari daerah kenaikan aset tinggi.
- **Pengusaha/Bisnis:** Mencari pasar besar & akses baik.
- **Developer Properti:** Mencari kawasan hunian baru.
- **UMKM:** Lokasi pasar terjangkau.
- **Pembeli Rumah & Pemerintah Daerah.**

## 7. Product Scope
- **Cakupan MVP:** 6 Provinsi (DKI, Banten, Jabar, Jateng, DIY, Jatim) -> Total 119 kota/kabupaten.
- **In Scope (MVP):** Dashboard, Peta interaktif, Detail wilayah, Perbandingan (2-4 wilayah), Filter/Search, AI Insight (summary), Halaman metodologi.
- **Out of Scope:** Prediksi harga ML, Simulasi ROI, Integrasi portal listing (Rumah123, dll), Fitur Login, Export PDF, Auto-update scraping.

## 19. Risks and Limitations
- **Data Gap:** BPS tidak lengkap untuk semua kabupaten (mitigasi: catat gap data).
- **Harga Properti Usang:** (mitigasi: validasi minimal 2 sumber).
- **Halusinasi AI:** (mitigasi: system prompt ketat hanya baca indikator yang disediakan).

## 20. Success Metrics
- **Data:** 90% indikator terisi (Target 6 bulan).
- **Traffic:** 500 MAU -> 2000 MAU, >3 menit per sesi.

## 22. Final Summary
Platform dikembangkan 3-5 bulan untuk jadi alat referensi andal menggunakan tech-stack Next.js, FastAPI, PostgreSQL, dan LLM (Claude API).
