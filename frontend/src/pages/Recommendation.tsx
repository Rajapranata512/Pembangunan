import { useState } from 'react';
import { Link } from 'react-router-dom';
import { getRecommendations } from '../api';
import type { RecommendationItem } from '../types';
import { getScoreColor, GOALS } from '../types';

export default function Recommendation() {
  const [goal, setGoal] = useState('');
  const [province, setProvince] = useState('');
  const [results, setResults] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const search = () => {
    if(!goal) return;
    setLoading(true); setSearched(true);
    getRecommendations({goal, province: province||undefined})
      .then(d => setResults(d.results))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  return (
    <div className="page"><div className="container">
      <div className="section-header">
        <div>
          <h1 className="section-title">Rekomendasi Wilayah</h1>
          <p className="section-subtitle">Temukan wilayah terbaik berdasarkan tujuan investasi Anda</p>
        </div>
      </div>

      <div className="card" style={{marginBottom:'2rem',padding:'2rem'}}>
        <div style={{display:'flex',gap:'12px',flexWrap:'wrap',alignItems:'flex-end'}}>
          <div style={{flex:1,minWidth:240}}>
            <label style={{display:'block',fontSize:'0.78rem',fontWeight:600,color:'#94a3b8',marginBottom:'6px',textTransform:'uppercase',letterSpacing:'0.05em'}}>
              Tujuan Investasi
            </label>
            <select value={goal} onChange={e=>setGoal(e.target.value)}
              style={{width:'100%',padding:'12px',background:'rgba(255,255,255,0.06)',color:'#f1f5f9',border:'1px solid rgba(255,255,255,0.1)',borderRadius:'8px',fontFamily:'Inter',fontSize:'0.9rem'}}>
              <option value="">Pilih tujuan...</option>
              {GOALS.map(g=><option key={g.value} value={g.value}>{g.label}</option>)}
            </select>
          </div>
          <div style={{minWidth:200}}>
            <label style={{display:'block',fontSize:'0.78rem',fontWeight:600,color:'#94a3b8',marginBottom:'6px',textTransform:'uppercase',letterSpacing:'0.05em'}}>
              Provinsi (Opsional)
            </label>
            <select value={province} onChange={e=>setProvince(e.target.value)}
              style={{width:'100%',padding:'12px',background:'rgba(255,255,255,0.06)',color:'#f1f5f9',border:'1px solid rgba(255,255,255,0.1)',borderRadius:'8px',fontFamily:'Inter',fontSize:'0.9rem'}}>
              <option value="">Semua Provinsi</option>
              <option value="Jawa Timur">Jawa Timur</option>
              <option value="Jawa Barat">Jawa Barat</option>
              <option value="Jawa Tengah">Jawa Tengah</option>
              <option value="DI Yogyakarta">DI Yogyakarta</option>
              <option value="Banten">Banten</option>
            </select>
          </div>
          <button onClick={search} className="btn btn-primary" style={{height:'fit-content'}}>
            Cari Rekomendasi
          </button>
        </div>
      </div>

      {loading && <div className="loading"><div className="spinner"/>Mencari rekomendasi terbaik...</div>}

      {!loading && searched && results.length === 0 && (
        <p style={{color:'#64748b',textAlign:'center'}}>Tidak ada hasil. Coba ubah filter.</p>
      )}

      <div style={{display:'flex',flexDirection:'column',gap:'1rem'}}>
        {results.map((item, i) => (
          <div key={item.rank} className="rec-card animate-in" style={{animationDelay:`${i*0.1}s`}}>
            <div className="rec-rank">{item.rank}</div>
            <div className="rec-info">
              <h3><Link to={`/region/${item.region.id}`}>{item.region.name}</Link></h3>
              <div className="rec-province">{item.region.province} &middot; {item.region.region_type}</div>
              <div className="rec-reason">{item.reason}</div>
              <div style={{display:'flex',gap:'8px',marginTop:'10px',flexWrap:'wrap'}}>
                <span className="score-badge" style={{background:`${getScoreColor(item.region.business_score)}18`,color:getScoreColor(item.region.business_score)}}>
                  Biz {item.region.business_score?.toFixed(0)}
                </span>
                <span className="score-badge" style={{background:`${getScoreColor(item.region.property_score)}18`,color:getScoreColor(item.region.property_score)}}>
                  Prop {item.region.property_score?.toFixed(0)}
                </span>
                <span className="score-badge" style={{background:`${getScoreColor(item.region.growth_score)}18`,color:getScoreColor(item.region.growth_score)}}>
                  Growth {item.region.growth_score?.toFixed(0)}
                </span>
                <span className="score-badge" style={{background:`${getScoreColor(item.region.risk_score)}18`,color:getScoreColor(item.region.risk_score)}}>
                  Risk {item.region.risk_score?.toFixed(0)}
                </span>
              </div>
            </div>
            <div className="rec-score">{item.relevance_score.toFixed(1)}</div>
          </div>
        ))}
      </div>
    </div></div>
  );
}
