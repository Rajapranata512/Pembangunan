# Bagian 3: Data Requirements & Scoring Methodology
**Proyek:** Platform Analisis Prospek Wilayah Jawa

## 10. Data Requirements
Sumber data dan prioritas pengumpulan untuk 119 kota/kabupaten di Jawa:
- **Demografi [Prioritas Tinggi]:** BPS (Jumlah populasi, pertumbuhan YoY, kepadatan, rasio usia produktif).
- **Ekonomi [Prioritas Tinggi]:** BPS (PDRB, pertumbuhan ekonomi YoY, PDRB per kapita, tingkat pengangguran terbuka).
- **Infrastruktur [Prioritas Tinggi]:** OpenStreetMap, BPJT (Jarak ke gerbang tol, stasiun, bandara).
- **Properti [Prioritas Tinggi]:** Rumah123, BI (Harga tanah/m2, harga rumah rata-rata, tren kenaikan YoY).
- **Fasilitas Publik [Prioritas Sedang]:** Kemdikbud, Google Maps (Jumlah sekolah, RS, kampus, pasar).
- **Kawasan Strategis [Prioritas Tinggi]:** BKPM, KPPIP, Bappenas (Kawasan Industri, KEK, Proyek Strategis Nasional).

## 11. Scoring Methodology
Skala 0-100 menggunakan metode Min-Max Scaling untuk normalisasi. Skor bersifat komparatif antarseluruh wilayah Pulau Jawa.

### A. Business Potential Score (30% dari Final)
- Jumlah penduduk (20%)
- PDRB per kapita (20%)
- Kepadatan penduduk (15%)
- Skor aksesibilitas infrastruktur (15%)
- Jumlah fasilitas publik (15%)
- Pertumbuhan ekonomi (15%)

### B. Property Investment Score (30% dari Final)
- Skor infrastruktur (Tol/Kereta/Bandara) (25%)
- Pertumbuhan penduduk YoY (20%)
- Pertumbuhan ekonomi YoY (20%)
- Indeks keterjangkauan harga properti (15%)
- Fasilitas publik (10%)
- Rencana pembangunan infrastruktur (10%)

### C. Regional Growth Score (25% dari Final)
- Pertumbuhan ekonomi YoY (25%)
- Pertumbuhan penduduk YoY (20%)
- Pembangunan infrastruktur baru (20%)
- Keberadaan kawasan industri/KEK (15%)
- Rencana pembangunan strategis (10%)
- Pertumbuhan fasilitas publik (10%)

### D. Investment Risk Score (15% dari Final, Di-inversi)
*Note: Skor TINGGI = Risiko LEBIH BESAR. Saat masuk Final Score dihitung `(100 - Risk Score)`.*
- Harga properti sudah terlalu tinggi (25%)
- Pertumbuhan ekonomi stagnan/rendah (20%)
- Pertumbuhan penduduk negatif/stagnan (15%)
- Infrastruktur kurang memadai (15%)
- Ketergantungan pada satu sektor ekonomi (10%)
- Tingkat pengangguran tinggi (10%)

**Formula Final Opportunity Score:**
`Final Score = (Business × 30%) + (Property × 30%) + (Growth × 25%) + (100 - Risk Score) × 15%`
