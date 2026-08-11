import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getRegionDetail } from '../api';
import type { RegionDetail as RD } from '../types';
import ScoreCard from '../components/ScoreCard';
import AiInsightPanel from '../components/AiInsightPanel';

export default function RegionDetail() {
  const { id } = useParams<{id:string}>();
  const [region, setRegion] = useState<RD|null>(null);
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if(id) {
      setLoading(true);
      getRegionDetail(Number(id)).then(setRegion).catch(console.error).finally(()=>setLoading(false));
    }
  }, [id]);

  if(loading) return <div className="page"><div className="container"><div className="loading"><div className="spinner"/>Memuat detail wilayah...</div></div></div>;
  if(!region) return <div className="page"><div className="container"><p>Wilayah tidak ditemukan.</p></div></div>;

  const s = region.scores[0];
  const d = region.demographics[0];
  const e = region.economy[0];
  const infra = region.infrastructure;
  const prop = region.property_market[0];
  const fac = region.facilities;
  const ai = region.ai_insight;

  const DataRow = ({label,value,unit=''}:{label:string,value:any,unit?:string}) => (
    <div className="data-item">
      <span className="data-item-label">{label}</span>
      <span className="data-item-value">
        {value !== null && value !== undefined
          ? `${typeof value==='number'?value.toLocaleString('id-ID'):value}${unit?` ${unit}`:''}`
          : '-'}
      </span>
    </div>
  );

  return (
    <div className="page"><div className="container">
      <div style={{marginBottom:'0.5rem'}}>
        <Link to="/dashboard" style={{fontSize:'0.85rem',color:'#64748b'}}>&larr; Kembali ke Dashboard</Link>
      </div>
      <div className="section-header">
        <div>
          <h1 className="section-title">{region.name}</h1>
          <p className="section-subtitle">
            {region.province} &middot; {region.region_type === 'kota' ? 'Kota' : 'Kabupaten'} &middot; {region.area_km2?.toLocaleString('id-ID')} km&sup2;
          </p>
        </div>
        <Link to={`/compare?ids=${region.id}`} className="btn btn-outline">Bandingkan</Link>
      </div>

      <div className="score-cards" style={{marginBottom:'2rem'}}>
        <ScoreCard label="Business" score={s?.business_score??null} delay={0}/>
        <ScoreCard label="Property" score={s?.property_score??null} delay={0.1}/>
        <ScoreCard label="Growth" score={s?.growth_score??null} delay={0.2}/>
        <ScoreCard label="Risk" score={s?.risk_score??null} delay={0.3}/>
        <ScoreCard label="Final Score" score={s?.final_score??null} delay={0.4}/>
      </div>

      <div className="tabs">
        {['overview','demografi','ekonomi','infrastruktur','properti','fasilitas'].map(t=>(
          <button key={t} className={`tab ${tab===t?'active':''}`} onClick={()=>setTab(t)}>
            {t.charAt(0).toUpperCase()+t.slice(1)}
          </button>
        ))}
      </div>

      {tab==='overview' && (
        <div>
          <AiInsightPanel
            regionId={region.id}
            regionName={region.name}
            initialInsight={ai}
          />

          {region.development_plans.length>0 && (
            <div style={{marginTop:'1.5rem'}}>
              <h3 style={{fontSize:'0.9rem',fontWeight:700,marginBottom:'10px'}}>Rencana Pembangunan</h3>
              {region.development_plans.map((p,i)=>(
                <div key={i} className="card" style={{marginBottom:'8px',padding:'1rem'}}>
                  <strong>{p.plan_name}</strong>
                  <div style={{fontSize:'0.82rem',color:'#94a3b8',marginTop:'4px'}}>
                    {p.plan_type} &middot; Status: {p.status} &middot; Target: {p.target_year} &middot; Impact: {p.impact_score}/10
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab==='demografi' && d && (
        <div className="card">
          <DataRow label="Jumlah Penduduk" value={d.population} unit="jiwa"/>
          <DataRow label="Pertumbuhan Penduduk" value={d.population_growth_pct} unit="%"/>
          <DataRow label="Kepadatan" value={d.density_per_km2} unit="jiwa/km&sup2;"/>
          <DataRow label="Usia Produktif" value={d.productive_age_count} unit="jiwa"/>
          <DataRow label="Jumlah Rumah Tangga" value={d.household_count}/>
          <DataRow label="Urbanisasi" value={d.urbanization_rate} unit="%"/>
        </div>
      )}

      {tab==='ekonomi' && e && (
        <div className="card">
          <DataRow label="PDRB" value={e.pdrb_billion_idr} unit="miliar Rp"/>
          <DataRow label="Pertumbuhan Ekonomi" value={e.economic_growth_pct} unit="%"/>
          <DataRow label="PDRB per Kapita" value={e.pdrb_per_capita} unit="Rp"/>
          <DataRow label="Pengangguran" value={e.unemployment_rate} unit="%"/>
          <DataRow label="Kemiskinan" value={e.poverty_rate} unit="%"/>
          <DataRow label="UMK" value={e.minimum_wage_idr} unit="Rp"/>
        </div>
      )}

      {tab==='infrastruktur' && infra && (
        <div className="card">
          <DataRow label="Jarak Tol Terdekat" value={infra.nearest_toll_gate_km} unit="km"/>
          <DataRow label="Skor Akses Tol" value={infra.toll_access_score}/>
          <DataRow label="Jarak Stasiun" value={infra.nearest_station_km} unit="km"/>
          <DataRow label="Skor Kereta" value={infra.railway_score}/>
          <DataRow label="Jarak Bandara" value={infra.nearest_airport_km} unit="km"/>
          <DataRow label="Transportasi Publik" value={infra.public_transport_score}/>
          <DataRow label="Kualitas Jalan" value={infra.road_quality_score}/>
          <DataRow label="Skor Komposit" value={infra.infrastructure_composite_score}/>
        </div>
      )}

      {tab==='properti' && prop && (
        <div className="card">
          <DataRow label="Harga Tanah Rata-rata" value={prop.avg_land_price_per_m2} unit="Rp/m&sup2;"/>
          <DataRow label="Harga Rumah Rata-rata" value={prop.avg_house_price} unit="Rp"/>
          <DataRow label="Kenaikan Harga" value={prop.property_price_growth_pct} unit="%/tahun"/>
          <DataRow label="Jumlah Listing" value={prop.listing_count}/>
          <DataRow label="Skor Keterjangkauan" value={prop.affordability_score}/>
        </div>
      )}

      {tab==='fasilitas' && fac && (
        <div className="card">
          <DataRow label="Sekolah" value={fac.school_count}/>
          <DataRow label="Perguruan Tinggi" value={fac.university_count}/>
          <DataRow label="Rumah Sakit" value={fac.hospital_count}/>
          <DataRow label="Klinik" value={fac.clinic_count}/>
          <DataRow label="Mall" value={fac.mall_count}/>
          <DataRow label="Pasar Tradisional" value={fac.traditional_market_count}/>
          <DataRow label="Hotel" value={fac.hotel_count}/>
          <DataRow label="Destinasi Wisata" value={fac.tourism_spot_count}/>
          <DataRow label="Skor Fasilitas" value={fac.facilities_composite_score}/>
        </div>
      )}
    </div></div>
  );
}
