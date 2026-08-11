/* ===================================================
   types.ts — TypeScript interfaces matching backend API
   =================================================== */

export interface RegionSummary {
  id: number;
  bps_code: string;
  name: string;
  province: string;
  region_type: string;
  latitude: number | null;
  longitude: number | null;
  business_score: number | null;
  property_score: number | null;
  growth_score: number | null;
  risk_score: number | null;
  final_score: number | null;
}

export interface PaginatedRegions {
  total: number;
  page: number;
  limit: number;
  data: RegionSummary[];
}

export interface DemographicData {
  year: number;
  population: number | null;
  population_growth_pct: number | null;
  density_per_km2: number | null;
  productive_age_count: number | null;
  household_count: number | null;
  urbanization_rate: number | null;
}

export interface EconomyData {
  year: number;
  pdrb_billion_idr: number | null;
  economic_growth_pct: number | null;
  pdrb_per_capita: number | null;
  unemployment_rate: number | null;
  poverty_rate: number | null;
  minimum_wage_idr: number | null;
}

export interface InfrastructureData {
  nearest_toll_gate_km: number | null;
  toll_access_score: number | null;
  nearest_station_km: number | null;
  railway_score: number | null;
  nearest_airport_km: number | null;
  nearest_port_km: number | null;
  public_transport_score: number | null;
  road_quality_score: number | null;
  infrastructure_composite_score: number | null;
}

export interface PropertyMarketData {
  year: number;
  avg_land_price_per_m2: number | null;
  avg_house_price: number | null;
  property_price_growth_pct: number | null;
  listing_count: number | null;
  affordability_score: number | null;
}

export interface FacilityData {
  school_count: number | null;
  university_count: number | null;
  hospital_count: number | null;
  clinic_count: number | null;
  mall_count: number | null;
  traditional_market_count: number | null;
  hotel_count: number | null;
  tourism_spot_count: number | null;
  facilities_composite_score: number | null;
}

export interface StrategicAreaData {
  has_industrial_estate: boolean;
  industrial_estate_names: string | null;
  has_kek: boolean;
  has_tourism_area: boolean;
  has_education_hub: boolean;
  has_tod: boolean;
  strategic_score: number | null;
}

export interface DevelopmentPlanData {
  plan_type: string | null;
  plan_name: string | null;
  status: string | null;
  target_year: number | null;
  impact_score: number | null;
  source: string | null;
}

export interface ScoreData {
  year: number;
  business_score: number | null;
  property_score: number | null;
  growth_score: number | null;
  risk_score: number | null;
  final_score: number | null;
  data_completeness_pct: number | null;
}

export interface AiInsightData {
  insight_text: string | null;
  key_strengths: string | null;
  key_risks: string | null;
  best_for: string | null;
}

export interface RegionDetail {
  id: number;
  bps_code: string;
  name: string;
  province: string;
  province_code: string | null;
  region_type: string;
  area_km2: number | null;
  latitude: number | null;
  longitude: number | null;
  demographics: DemographicData[];
  economy: EconomyData[];
  infrastructure: InfrastructureData | null;
  property_market: PropertyMarketData[];
  facilities: FacilityData | null;
  strategic_area: StrategicAreaData | null;
  development_plans: DevelopmentPlanData[];
  scores: ScoreData[];
  ai_insight: AiInsightData | null;
}

export interface MapDataPoint {
  id: number;
  name: string;
  province: string;
  region_type: string;
  latitude: number | null;
  longitude: number | null;
  business_score: number | null;
  property_score: number | null;
  growth_score: number | null;
  risk_score: number | null;
  final_score: number | null;
}

export interface RecommendationItem {
  rank: number;
  region: RegionSummary;
  relevance_score: number;
  reason: string;
}

export interface RecommendationResponse {
  goal: string;
  results: RecommendationItem[];
}

/* Score color helper */
export function getScoreColor(score: number | null): string {
  if (score === null) return '#6b7280';
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#3b82f6';
  if (score >= 40) return '#eab308';
  if (score >= 20) return '#f97316';
  return '#ef4444';
}

export function getScoreLabel(score: number | null): string {
  if (score === null) return 'N/A';
  if (score >= 80) return 'Sangat Potensial';
  if (score >= 60) return 'Potensial';
  if (score >= 40) return 'Moderat';
  if (score >= 20) return 'Terbatas';
  return 'Kurang Menarik';
}

export const GOALS = [
  { value: 'membuka_usaha_kuliner', label: 'Membuka Usaha Kuliner' },
  { value: 'membuka_ruko_komersial', label: 'Membuka Ruko / Usaha Komersial' },
  { value: 'membeli_tanah_investasi', label: 'Membeli Tanah untuk Investasi' },
  { value: 'membeli_rumah_hunian', label: 'Membeli Rumah untuk Hunian' },
  { value: 'properti_disewakan', label: 'Properti untuk Disewakan' },
  { value: 'gudang_logistik', label: 'Gudang / Logistik' },
  { value: 'usaha_dekat_kampus', label: 'Usaha Dekat Kampus' },
  { value: 'usaha_dekat_industri', label: 'Usaha Dekat Kawasan Industri' },
  { value: 'daerah_berkembang_terjangkau', label: 'Daerah Berkembang & Terjangkau' },
  { value: 'risiko_rendah', label: 'Risiko Investasi Rendah' },
];

/* Chat types */
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

/* Sentiment types */
export interface SentimentHighlight {
  headline: string;
  sentiment: string;
  reason: string;
}

export interface SentimentData {
  overall_sentiment: string;
  confidence_score: number;
  summary: string;
  highlights: SentimentHighlight[];
  headlines: string[];
  cached: boolean;
}

/* Generate Insight response */
export interface GenerateInsightResponse {
  success: boolean;
  message: string;
  insight: AiInsightData | null;
}

