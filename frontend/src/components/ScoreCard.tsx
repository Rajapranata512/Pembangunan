import { getScoreColor, getScoreLabel } from '../types';

interface Props { label: string; score: number | null; delay?: number; }

export default function ScoreCard({ label, score, delay = 0 }: Props) {
  const color = getScoreColor(score);
  const badge = getScoreLabel(score);
  return (
    <div className="score-card animate-in" style={{ animationDelay: `${delay}s` }}>
      <div className="score-card-label">{label}</div>
      <div className="score-card-value" style={{ color }}>{score !== null ? score.toFixed(1) : 'N/A'}</div>
      <span className="score-card-badge" style={{ background: `${color}18`, color }}>{badge}</span>
      <div style={{ position:'absolute', bottom:0, left:0, right:0, height:3, background:color }} />
    </div>
  );
}
