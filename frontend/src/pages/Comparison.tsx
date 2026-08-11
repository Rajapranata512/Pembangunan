import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getRegions, compareRegions } from '../api';
import type { RegionSummary, RegionDetail } from '../types';
import { getScoreColor } from '../types';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from 'recharts';

const COLORS = ['#3b82f6','#8b5cf6','#22c55e','#f59e0b'];

export default function Comparison() {
  const [searchParams] = useSearchParams();
  const [allRegions, setAllRegions] = useState<RegionSummary[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [compared, setCompared] = useState<RegionDetail[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getRegions({limit:150}).then(d=>setAllRegions(d.data));
    const idsParam = searchParams.get('ids');
    if(idsParam) setSelectedIds(idsParam.split(',').map(Number).filter(Boolean));
  }, []);

  useEffect(() => {
    if(selectedIds.length >= 2) {
      setLoading(true);
      compareRegions(selectedIds).then(setCompared).catch(console.error).finally(()=>setLoading(false));
    } else { setCompared([]); }
  }, [selectedIds]);

  const toggleRegion = (id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x=>x!==id) : prev.length < 4 ? [...prev, id] : prev
    );
  };

  const radarData = compared.length ? [
    {metric:'Business',...Object.fromEntries(compared.map((_r,i)=>[`r${i}`,compared[i].scores[0]?.business_score??0]))},
    {metric:'Property',...Object.fromEntries(compared.map((_r,i)=>[`r${i}`,compared[i].scores[0]?.property_score??0]))},
    {metric:'Growth',...Object.fromEntries(compared.map((_r,i)=>[`r${i}`,compared[i].scores[0]?.growth_score??0]))},
    {metric:'Safety',...Object.fromEntries(compared.map((_r,i)=>[`r${i}`,100-(compared[i].scores[0]?.risk_score??50)]))},
  ] : [];

  const barData = compared.length ? [
    {name:'Business',...Object.fromEntries(compared.map(r=>[r.name,r.scores[0]?.business_score??0]))},
    {name:'Property',...Object.fromEntries(compared.map(r=>[r.name,r.scores[0]?.property_score??0]))},
    {name:'Growth',...Object.fromEntries(compared.map(r=>[r.name,r.scores[0]?.growth_score??0]))},
    {name:'Risk',...Object.fromEntries(compared.map(r=>[r.name,r.scores[0]?.risk_score??0]))},
    {name:'Final',...Object.fromEntries(compared.map(r=>[r.name,r.scores[0]?.final_score??0]))},
  ] : [];

  return (
    <div className="page"><div className="container">
      <div className="section-header">
        <div>
          <h1 className="section-title">Perbandingan Wilayah</h1>
          <p className="section-subtitle">Pilih 2-4 wilayah untuk membandingkan skor dan indikator</p>
        </div>
      </div>

      <div className="card" style={{marginBottom:'1.5rem'}}>
        <p style={{fontSize:'0.85rem',color:'#94a3b8',marginBottom:'12px'}}>
          Pilih wilayah (maks 4): <strong style={{color:'#60a5fa'}}>{selectedIds.length}</strong> dipilih
        </p>
        <div style={{display:'flex',flexWrap:'wrap',gap:'8px'}}>
          {allRegions.map(r=>(
            <button key={r.id} onClick={()=>toggleRegion(r.id)}
              style={{
                padding:'6px 14px', borderRadius:'20px', cursor:'pointer',
                border: selectedIds.includes(r.id)?'1px solid #3b82f6':'1px solid rgba(255,255,255,0.1)',
                background: selectedIds.includes(r.id)?'rgba(59,130,246,0.15)':'rgba(255,255,255,0.04)',
                color: selectedIds.includes(r.id)?'#60a5fa':'#94a3b8',
                fontSize:'0.82rem', fontFamily:'Inter', fontWeight:500, transition:'all 0.2s',
              }}>
              {r.name}
            </button>
          ))}
        </div>
      </div>

      {selectedIds.length < 2 && selectedIds.length > 0 && (
        <p style={{color:'#64748b',textAlign:'center',padding:'2rem 0'}}>Pilih minimal 2 wilayah untuk mulai perbandingan.</p>
      )}

      {loading && <div className="loading"><div className="spinner"/>Memuat perbandingan...</div>}

      {compared.length >= 2 && (
        <>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'1.5rem',marginBottom:'1.5rem'}}>
            <div className="chart-container">
              <h3 style={{fontSize:'0.9rem',fontWeight:700,marginBottom:'1rem'}}>Radar Perbandingan</h3>
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(255,255,255,0.08)"/>
                  <PolarAngleAxis dataKey="metric" tick={{fill:'#94a3b8',fontSize:12}}/>
                  <PolarRadiusAxis domain={[0,100]} tick={{fill:'#64748b',fontSize:10}}/>
                  {compared.map((r,i)=>(
                    <Radar key={r.id} name={r.name} dataKey={`r${i}`}
                      stroke={COLORS[i]} fill={COLORS[i]} fillOpacity={0.15} strokeWidth={2}/>
                  ))}
                  <Legend wrapperStyle={{fontSize:'0.8rem'}}/>
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <h3 style={{fontSize:'0.9rem',fontWeight:700,marginBottom:'1rem'}}>Skor per Kategori</h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)"/>
                  <XAxis dataKey="name" tick={{fill:'#94a3b8',fontSize:11}}/>
                  <YAxis domain={[0,100]} tick={{fill:'#64748b',fontSize:10}}/>
                  <Tooltip contentStyle={{background:'#1e293b',border:'1px solid rgba(255,255,255,0.1)',borderRadius:8,fontSize:'0.82rem'}}/>
                  {compared.map((r,i)=>(
                    <Bar key={r.id} dataKey={r.name} fill={COLORS[i]} radius={[4,4,0,0]}/>
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead><tr>
                <th>Indikator</th>
                {compared.map(r=><th key={r.id}>{r.name}</th>)}
              </tr></thead>
              <tbody>
                <tr><td>Final Score</td>{compared.map(r=>(
                  <td key={r.id}><span className="score-badge" style={{background:`${getScoreColor(r.scores[0]?.final_score??null)}18`,color:getScoreColor(r.scores[0]?.final_score??null)}}>{r.scores[0]?.final_score?.toFixed(1)}</span></td>
                ))}</tr>
                <tr><td>Business Score</td>{compared.map(r=>(
                  <td key={r.id}><span className="score-badge" style={{background:`${getScoreColor(r.scores[0]?.business_score??null)}18`,color:getScoreColor(r.scores[0]?.business_score??null)}}>{r.scores[0]?.business_score?.toFixed(1)}</span></td>
                ))}</tr>
                <tr><td>Populasi</td>{compared.map(r=><td key={r.id}>{r.demographics[0]?.population?.toLocaleString('id-ID')??'-'}</td>)}</tr>
                <tr><td>PDRB (miliar Rp)</td>{compared.map(r=><td key={r.id}>{r.economy[0]?.pdrb_billion_idr?.toLocaleString('id-ID')??'-'}</td>)}</tr>
                <tr><td>PDRB per Kapita</td>{compared.map(r=><td key={r.id}>{r.economy[0]?.pdrb_per_capita?.toLocaleString('id-ID')??'-'}</td>)}</tr>
                <tr><td>Harga Tanah/m&sup2;</td>{compared.map(r=><td key={r.id}>{r.property_market[0]?.avg_land_price_per_m2?.toLocaleString('id-ID')??'-'}</td>)}</tr>
                <tr><td>Skor Infrastruktur</td>{compared.map(r=><td key={r.id}>{r.infrastructure?.infrastructure_composite_score??'-'}</td>)}</tr>
                <tr><td>Skor Fasilitas</td>{compared.map(r=><td key={r.id}>{r.facilities?.facilities_composite_score??'-'}</td>)}</tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </div></div>
  );
}
