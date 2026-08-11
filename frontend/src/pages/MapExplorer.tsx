import { useState, useEffect } from 'react';
import { getMapData } from '../api';
import type { MapDataPoint } from '../types';
import MapView from '../components/MapView';

export default function MapExplorer() {
  const [data, setData] = useState<MapDataPoint[]>([]);
  const [scoreType, setScoreType] = useState('final_score');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMapData().then(setData).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <div className="page"><div className="container">
      <div className="section-header">
        <div>
          <h1 className="section-title">Peta Interaktif</h1>
          <p className="section-subtitle">Eksplorasi potensi wilayah Pulau Jawa secara visual</p>
        </div>
        <div className="map-controls">
          <select value={scoreType} onChange={e=>setScoreType(e.target.value)} style={{background:'rgba(255,255,255,0.06)',color:'#f1f5f9',border:'1px solid rgba(255,255,255,0.1)',borderRadius:'8px',padding:'8px 12px',fontFamily:'Inter',fontSize:'0.85rem'}}>
            <option value="final_score">Final Score</option>
            <option value="business_score">Business Score</option>
            <option value="property_score">Property Score</option>
            <option value="growth_score">Growth Score</option>
            <option value="risk_score">Risk Score</option>
          </select>
        </div>
      </div>
      {loading ? <div className="loading"><div className="spinner"/>Memuat peta...</div> : <MapView data={data} scoreType={scoreType} height="calc(100vh - 200px)"/>}

      <div style={{display:'flex',gap:'12px',justifyContent:'center',marginTop:'1rem',flexWrap:'wrap'}}>
        {[{c:'#22c55e',l:'80-100 Sangat Potensial'},{c:'#3b82f6',l:'60-79 Potensial'},{c:'#eab308',l:'40-59 Moderat'},{c:'#f97316',l:'20-39 Terbatas'},{c:'#ef4444',l:'0-19 Kurang Menarik'}].map(x=>(
          <div key={x.l} style={{display:'flex',alignItems:'center',gap:'6px',fontSize:'0.78rem',color:'#94a3b8'}}>
            <div style={{width:12,height:12,borderRadius:'50%',background:x.c}}/>{x.l}
          </div>
        ))}
      </div>
    </div></div>
  );
}
