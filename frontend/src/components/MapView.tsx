import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import type { MapDataPoint } from '../types';
import { getScoreColor } from '../types';

interface Props { data: MapDataPoint[]; scoreType?: string; height?: string; }

export default function MapView({ data, scoreType = 'final_score', height = '600px' }: Props) {
  const nav = useNavigate();
  const getScore = (d: MapDataPoint) => {
    const key = scoreType as keyof MapDataPoint;
    return (d[key] as number | null) ?? null;
  };

  return (
    <div className="map-container" style={{ height }}>
      <MapContainer
        center={[-7.3, 110.4]}
        zoom={7}
        style={{ height: '100%', width: '100%', background: '#0d1324' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {data.filter(d => d.latitude && d.longitude).map(d => {
          const score = getScore(d);
          const color = getScoreColor(score);
          return (
            <CircleMarker
              key={d.id}
              center={[d.latitude!, d.longitude!]}
              radius={10}
              fillColor={color}
              color={color}
              weight={2}
              opacity={0.9}
              fillOpacity={0.6}
            >
              <Popup>
                <div style={{fontFamily:'Inter,sans-serif'}}>
                  <strong style={{fontSize:'0.95rem'}}>{d.name}</strong>
                  <div style={{color:'#9ca3af',fontSize:'0.8rem',margin:'4px 0'}}>{d.province} &middot; {d.region_type}</div>
                  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'4px 12px',fontSize:'0.82rem',margin:'8px 0'}}>
                    <span>Business:</span><strong style={{color:getScoreColor(d.business_score)}}>{d.business_score?.toFixed(1)??'-'}</strong>
                    <span>Property:</span><strong style={{color:getScoreColor(d.property_score)}}>{d.property_score?.toFixed(1)??'-'}</strong>
                    <span>Growth:</span><strong style={{color:getScoreColor(d.growth_score)}}>{d.growth_score?.toFixed(1)??'-'}</strong>
                    <span>Risk:</span><strong style={{color:getScoreColor(d.risk_score)}}>{d.risk_score?.toFixed(1)??'-'}</strong>
                    <span>Final:</span><strong style={{color:getScoreColor(d.final_score)}}>{d.final_score?.toFixed(1)??'-'}</strong>
                  </div>
                  <button onClick={()=>nav(`/region/${d.id}`)} style={{width:'100%',padding:'6px',background:'#3b82f6',color:'#fff',border:'none',borderRadius:'6px',cursor:'pointer',fontFamily:'Inter',fontWeight:600,fontSize:'0.8rem'}}>Lihat Detail</button>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
