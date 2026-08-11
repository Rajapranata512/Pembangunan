import { useState, useEffect } from 'react';
import { getRegions } from '../api';
import type { RegionSummary } from '../types';
import RegionTable from '../components/RegionTable';

export default function Dashboard() {
  const [regions, setRegions] = useState<RegionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [province, setProvince] = useState('');
  const [regionType, setRegionType] = useState('');

  useEffect(() => {
    setLoading(true);
    getRegions({ province: province||undefined, type: regionType||undefined, limit: 150 })
      .then(d => setRegions(d.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [province, regionType]);

  const topRegion = regions.length ? regions.reduce((a,b)=>(a.final_score??0)>(b.final_score??0)?a:b) : null;
  const avgScore = regions.length ? (regions.reduce((s,r)=>s+(r.final_score??0),0)/regions.length).toFixed(1) : '0';
  const topBusiness = regions.length ? regions.reduce((a,b)=>(a.business_score??0)>(b.business_score??0)?a:b) : null;
  const topGrowth = regions.length ? regions.reduce((a,b)=>(a.growth_score??0)>(b.growth_score??0)?a:b) : null;

  return (
    <div className="page"><div className="container">
      <div className="section-header">
        <div>
          <h1 className="section-title">Dashboard Wilayah</h1>
          <p className="section-subtitle">Ranking dan analisis seluruh kota/kabupaten di Pulau Jawa</p>
        </div>
      </div>

      <div className="stats-grid" style={{marginBottom:'1.5rem'}}>
        <div className="stat-card animate-in"><div className="stat-label">Total Wilayah</div><div className="stat-value" style={{color:'#60a5fa'}}>{regions.length}</div><div className="stat-sub">kota & kabupaten</div></div>
        <div className="stat-card animate-in animate-in-delay-1"><div className="stat-label">Rata-rata Final Score</div><div className="stat-value" style={{color:'#a78bfa'}}>{avgScore}</div><div className="stat-sub">dari skala 0-100</div></div>
        <div className="stat-card animate-in animate-in-delay-2"><div className="stat-label">Top Performer</div><div className="stat-value" style={{color:'#22c55e',fontSize:'1.3rem'}}>{topRegion?.name??'-'}</div><div className="stat-sub">Skor {topRegion?.final_score?.toFixed(1)}</div></div>
        <div className="stat-card animate-in animate-in-delay-3"><div className="stat-label">Top Business</div><div className="stat-value" style={{color:'#f59e0b',fontSize:'1.3rem'}}>{topBusiness?.name??'-'}</div><div className="stat-sub">Skor {topBusiness?.business_score?.toFixed(1)}</div></div>
      </div>

      <div className="filter-bar">
        <select value={province} onChange={e=>setProvince(e.target.value)}>
          <option value="">Semua Provinsi</option>
          <option value="Jawa Timur">Jawa Timur</option>
          <option value="Jawa Barat">Jawa Barat</option>
          <option value="Jawa Tengah">Jawa Tengah</option>
          <option value="DI Yogyakarta">DI Yogyakarta</option>
          <option value="Banten">Banten</option>
          <option value="DKI Jakarta">DKI Jakarta</option>
        </select>
        <select value={regionType} onChange={e=>setRegionType(e.target.value)}>
          <option value="">Semua Tipe</option>
          <option value="kota">Kota</option>
          <option value="kabupaten">Kabupaten</option>
        </select>
      </div>

      {loading ? <div className="loading"><div className="spinner"/>Memuat data...</div> : <RegionTable regions={regions}/>}
    </div></div>
  );
}
