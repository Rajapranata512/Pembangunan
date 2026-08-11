# Bagian 4: Technical Architecture, DB & API
**Proyek:** Platform Analisis Prospek Wilayah Jawa

## 13. Database Design (PostgreSQL)
### Tabel Master
- `regions`: id (PK), bps_code, province, name, region_type (kota/kab), area_km2, lat, long, geojson_path.
### Tabel Indikator (Relasi 1:N ke regions, per tahun)
- `demographics`: year, population, growth_pct, density, productive_age, urbanization.
- `economy`: year, pdrb_billion, growth_pct, pdrb_per_capita, unemployment, poverty, minimum_wage.
- `infrastructure`: nearest_toll_km, toll_score, nearest_station, railway_score, nearest_airport.
- `property_market`: year, avg_land_price, avg_house_price, price_growth_pct, affordability_score.
- `facilities`: school_count, university_count, hospital_count, mall_count, tourism_spot.
### Tabel Penunjang
- `strategic_areas`: has_industrial_estate, has_kek, has_tod.
- `development_plans`: plan_type, name, status (planned/ongoing), target_year, impact_score.
### Tabel Output
- `scores`: year, business_score, property_score, growth_score, risk_score, final_score.
- `ai_insights`: insight_text, key_strengths, key_risks, best_for.

## 14. API Requirements (REST, Prefix: `/api/v1`)
- `GET /regions`: Daftar wilayah (Params: province, type, min_score, sort_by).
- `GET /regions/:id`: Detail semua indikator wilayah.
- `GET /regions/:id/scores`: Object khusus skor 4 kategori.
- `GET /regions/:id/insight`: String dan array insight AI.
- `GET /compare`: (Params: ids koma-dipisah) Kembalikan data perbandingan.
- `POST /recommendations`: Body JSON berisi `goal`, `filters` -> Response Top 5 wilayah.
- `GET /map-data`: Data minimal (id, lat, long, skor) untuk render peta GeoJSON.

## 16. Non-Functional Requirements
- **Performa:** Page load < 3 detik, Render Peta Leaflet < 4 detik, API latency < 500ms.
- **Keamanan:** Sanitasi input API, Rate limiting (100 req/min per IP), CORS strict domain.
- **Skalabilitas:** Pemisahan deployment Frontend dan Backend.
- **Aksesibilitas:** Mendukung desktop (1280px) dan mobile web (375px).

## 17. Tech Stack Recommendation
- **Frontend:** Next.js 14+ (App Router), TypeScript, Tailwind CSS, ShadCN UI, Recharts (Charts), React-Leaflet (Peta).
- **Backend:** Python FastAPI (REST API), Pandas & scikit-learn (Scoring engine MinMaxScaler).
- **Database:** PostgreSQL (Disarankan via Supabase untuk MVP).
- **AI Integration:** Anthropic Claude API (Generasi AI Insight teks).
- **Deployment:** Vercel (Frontend), Railway / Render (Backend).
