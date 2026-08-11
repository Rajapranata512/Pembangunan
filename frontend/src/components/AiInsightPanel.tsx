import { useState, useEffect } from 'react';
import { generateInsight, downloadReport, getSentiment } from '../api';
import type { AiInsightData, SentimentData } from '../types';

interface Props {
  regionId: number;
  regionName: string;
  initialInsight: AiInsightData | null;
}

export default function AiInsightPanel({ regionId, regionName, initialInsight }: Props) {
  const [insight, setInsight] = useState<AiInsightData | null>(initialInsight);
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [generating, setGenerating] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [loadingSentiment, setLoadingSentiment] = useState(false);
  const [showSentiment, setShowSentiment] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setInsight(initialInsight);
    setSentiment(null);
    setShowSentiment(false);
  }, [initialInsight, regionId]);

  let strengths: string[] = [];
  let risks: string[] = [];
  let bestFor: string[] = [];
  try { if (insight?.key_strengths) strengths = JSON.parse(insight.key_strengths); } catch { /* */ }
  try { if (insight?.key_risks) risks = JSON.parse(insight.key_risks); } catch { /* */ }
  try { if (insight?.best_for) bestFor = JSON.parse(insight.best_for); } catch { /* */ }

  const handleRegenerate = async () => {
    setGenerating(true);
    setError('');
    try {
      const res = await generateInsight(regionId);
      if (res.success && res.insight) {
        setInsight(res.insight);
      }
    } catch (e: any) {
      setError(e.message || 'Gagal generate insight');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      await downloadReport(regionId);
    } catch (e: any) {
      setError(e.message || 'Gagal download PDF');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleLoadSentiment = async () => {
    setShowSentiment(true);
    setLoadingSentiment(true);
    try {
      const data = await getSentiment(regionId);
      setSentiment(data);
    } catch (e: any) {
      setError(e.message || 'Gagal memuat sentimen');
    } finally {
      setLoadingSentiment(false);
    }
  };

  const sentimentColor = (s: string) => {
    if (s === 'positif') return '#22c55e';
    if (s === 'negatif') return '#ef4444';
    return '#eab308';
  };

  const sentimentEmoji = (s: string) => {
    if (s === 'positif') return '📈';
    if (s === 'negatif') return '📉';
    return '➖';
  };

  return (
    <div className="ai-panel">
      {/* Header */}
      <div className="ai-panel-header">
        <div className="ai-panel-badge">
          <span className="ai-panel-badge-dot"></span>
          AI Powered
        </div>
        <div className="ai-panel-actions">
          <button
            className="btn btn-outline ai-panel-btn"
            onClick={handleRegenerate}
            disabled={generating}
            title="Generate insight baru dengan AI"
          >
            {generating ? '⏳ Generating...' : '🔄 Regenerate AI'}
          </button>
          <button
            className="btn btn-outline ai-panel-btn"
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            title="Download laporan PDF"
          >
            {downloadingPdf ? '⏳ Membuat PDF...' : '📄 Download PDF'}
          </button>
        </div>
      </div>

      {error && (
        <div className="ai-panel-error">
          ⚠️ {error}
          <button onClick={() => setError('')} style={{marginLeft: 8, background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer'}}>✕</button>
        </div>
      )}

      {/* AI Insight Content */}
      {generating ? (
        <div className="ai-panel-skeleton">
          <div className="skeleton skeleton-line"></div>
          <div className="skeleton skeleton-line" style={{width: '90%'}}></div>
          <div className="skeleton skeleton-line" style={{width: '85%'}}></div>
          <div className="skeleton skeleton-line" style={{width: '70%'}}></div>
          <div className="skeleton skeleton-line" style={{width: '95%'}}></div>
          <div className="skeleton skeleton-line" style={{width: '80%'}}></div>
        </div>
      ) : insight ? (
        <>
          <div className="insight-box" style={{marginBottom: '1.5rem'}}>
            <h3>🤖 Analisis AI — {regionName}</h3>
            <p style={{whiteSpace: 'pre-line'}}>{insight.insight_text}</p>
          </div>

          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
            {strengths.length > 0 && (
              <div className="card">
                <h3 style={{fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px', color: '#22c55e'}}>
                  ✅ Kekuatan Utama
                </h3>
                <div className="tags">
                  {strengths.map((s, i) => <span key={i} className="tag tag-green">{s}</span>)}
                </div>
              </div>
            )}
            {risks.length > 0 && (
              <div className="card">
                <h3 style={{fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px', color: '#ef4444'}}>
                  ⚠️ Risiko Utama
                </h3>
                <div className="tags">
                  {risks.map((r, i) => <span key={i} className="tag tag-red">{r}</span>)}
                </div>
              </div>
            )}
          </div>

          {bestFor.length > 0 && (
            <div style={{marginTop: '1rem'}}>
              <h3 style={{fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px', color: '#60a5fa'}}>
                🎯 Paling Cocok Untuk
              </h3>
              <div className="tags">
                {bestFor.map((b, i) => <span key={i} className="tag">{b}</span>)}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="ai-panel-empty">
          <p>Belum ada AI insight. Klik "Regenerate AI" untuk membuat analisis baru.</p>
        </div>
      )}

      {/* Sentiment Section */}
      <div style={{marginTop: '1.5rem'}}>
        {!showSentiment ? (
          <button
            className="btn btn-outline ai-panel-btn"
            onClick={handleLoadSentiment}
            style={{width: '100%'}}
          >
            📰 Lihat Sentimen Berita Terkini
          </button>
        ) : loadingSentiment ? (
          <div className="ai-panel-skeleton">
            <div className="skeleton skeleton-line" style={{width: '50%'}}></div>
            <div className="skeleton skeleton-line"></div>
            <div className="skeleton skeleton-line" style={{width: '80%'}}></div>
          </div>
        ) : sentiment ? (
          <div className="sentiment-section">
            <div className="sentiment-header">
              <h3 style={{fontSize: '0.95rem', fontWeight: 700}}>
                📰 Sentimen Berita — {regionName}
              </h3>
              <span
                className="sentiment-badge"
                style={{
                  background: `${sentimentColor(sentiment.overall_sentiment)}18`,
                  color: sentimentColor(sentiment.overall_sentiment),
                  border: `1px solid ${sentimentColor(sentiment.overall_sentiment)}40`,
                }}
              >
                {sentimentEmoji(sentiment.overall_sentiment)} {sentiment.overall_sentiment.toUpperCase()}
                {sentiment.confidence_score > 0 && ` (${(sentiment.confidence_score * 100).toFixed(0)}%)`}
              </span>
            </div>

            {sentiment.summary && (
              <p style={{fontSize: '0.88rem', color: '#94a3b8', margin: '8px 0 12px', lineHeight: 1.6}}>
                {sentiment.summary}
              </p>
            )}

            {sentiment.highlights.length > 0 && (
              <div className="sentiment-highlights">
                {sentiment.highlights.map((h, i) => (
                  <div key={i} className="sentiment-highlight-item">
                    <span className="sentiment-highlight-dot" style={{background: sentimentColor(h.sentiment)}}></span>
                    <div>
                      <div style={{fontSize: '0.85rem', fontWeight: 600}}>{h.headline}</div>
                      {h.reason && <div style={{fontSize: '0.78rem', color: '#64748b', marginTop: 2}}>{h.reason}</div>}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {sentiment.cached && (
              <div style={{fontSize: '0.72rem', color: '#64748b', marginTop: 8}}>
                📦 Data dari cache (diperbarui setiap 24 jam)
              </div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
