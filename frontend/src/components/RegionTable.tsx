import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { RegionSummary } from '../types';
import { getScoreColor } from '../types';

interface Props { regions: RegionSummary[]; }
type SortKey = 'final_score'|'business_score'|'property_score'|'growth_score'|'risk_score'|'name';

export default function RegionTable({ regions }: Props) {
  const nav = useNavigate();
  const [sortBy, setSortBy] = useState<SortKey>('final_score');
  const [asc, setAsc] = useState(false);

  const toggle = (key: SortKey) => {
    if (sortBy === key) setAsc(!asc);
    else { setSortBy(key); setAsc(key === 'name'); }
  };

  const sorted = [...regions].sort((a, b) => {
    const av = a[sortBy] ?? 0, bv = b[sortBy] ?? 0;
    if (typeof av === 'string') return asc ? (av as string).localeCompare(bv as string) : (bv as string).localeCompare(av as string);
    return asc ? (av as number) - (bv as number) : (bv as number) - (av as number);
  });

  const Badge = ({v}:{v:number|null}) => (
    <span className="score-badge" style={{background:`${getScoreColor(v)}18`,color:getScoreColor(v)}}>
      {v !== null ? v.toFixed(1) : '-'}
    </span>
  );

  const TH = ({k,children}:{k:SortKey,children:React.ReactNode}) => (
    <th onClick={()=>toggle(k)} className={sortBy===k?'sorted':''}>
      {children} {sortBy===k?(asc?'\u2191':'\u2193'):''}
    </th>
  );

  return (
    <div className="table-wrap">
      <table>
        <thead><tr>
          <th>#</th>
          <TH k="name">Wilayah</TH>
          <th>Provinsi</th>
          <TH k="business_score">Business</TH>
          <TH k="property_score">Property</TH>
          <TH k="growth_score">Growth</TH>
          <TH k="risk_score">Risk</TH>
          <TH k="final_score">Final</TH>
        </tr></thead>
        <tbody>
          {sorted.map((r, i) => (
            <tr key={r.id}>
              <td>{i+1}</td>
              <td className="region-name" onClick={()=>nav(`/region/${r.id}`)}>{r.name}</td>
              <td>{r.province}</td>
              <td><Badge v={r.business_score}/></td>
              <td><Badge v={r.property_score}/></td>
              <td><Badge v={r.growth_score}/></td>
              <td><Badge v={r.risk_score}/></td>
              <td><Badge v={r.final_score}/></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
