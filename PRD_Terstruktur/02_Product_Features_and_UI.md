# Bagian 2: Product Features, User Flow & UI/UX
**Proyek:** Platform Analisis Prospek Wilayah Jawa

## 8. Core Features
1. **Dashboard Utama:** KPI cards, Tabel Ranking, Mini Map, Widget top 10.
2. **Peta Interaktif (Map Explorer):** Visual warna berdasar skor, layer toggle (Tol, Kawasan Industri, dll), klik untuk pop-up ringkasan.
3. **Region Detail:** Skor KPI wilayah, Tab Data indikator lengkap, daftar kawasan strategis terdekat, AI Insight (3-5 kalimat), Rekomendasi peruntukan.
4. **Comparison:** Tabel skor banding 2-4 wilayah, radar/bar chart untuk analisis multidimensi.
5. **Recommendation Engine:** Berdasarkan 10 tujuan default (e.g. Buka Kuliner, Investasi Gudang) -> menghasilkan Top 5 wilayah.
6. **AI Insight:** Summary berbasis LLM untuk mendeskripsikan indikator, kekuatan & risiko wilayah.
7. **Filter & Search:** Provinsi, rentang skor, jumlah penduduk, tipe wilayah (kota/kabupaten).

## 9. User Flow
1. **Melihat Ranking:** Home -> Dashboard Filter -> Urutkan Tabel -> Buka Detail Wilayah.
2. **Membandingkan Wilayah:** Halaman Detail/Bandingkan -> Pilih max 4 wilayah -> Lihat Radar Chart & Tabel.
3. **Mencari Rekomendasi:** Halaman Rekomendasi -> Pilih Tujuan Investasi -> Sistem tampilkan Top 5 -> Buka Detail.
4. **Eksplorasi Peta:** Halaman Map -> Ganti Layer Skor -> Klik Wilayah -> Buka Pop-up.

## 12. Page Structure
- **Home:** Landing page, Hero banner, CTA.
- **Dashboard:** Ringkasan KPI nasional, tabel filterable, mini map.
- **Map Explorer:** Halaman penuh peta Leaflet/Mapbox interaktif.
- **Region Detail:** Profil wilayah dengan tab indikator dan insight AI.
- **Comparison:** Halaman pencarian dan perbandingan multi-wilayah.
- **Recommendation:** Form input tujuan dan daftar hasil rekomendasi.
- **Data Source:** Halaman transparansi metode skoring dan sumber data.

## 15. UI/UX Guidelines
- **Prinsip Utama:** Simple, Data-first, Mobile-responsive, Progressive disclosure (tampilkan ringkasan dulu).
- **Color System (Skor):** 
  - Hijau (80-100): Sangat Potensial
  - Biru (60-79): Potensial
  - Kuning (40-59): Moderat
  - Oranye (20-39): Terbatas
  - Merah (0-19): Kurang Menarik
- **Typography:** Font utama Inter / Geist (Sistem Next.js).
