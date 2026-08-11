import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="page">
      <section className="hero">
        <div className="hero-content">
          <h1>Temukan Lokasi Terbaik untuk Investasi di Pulau Jawa</h1>
          <p>Platform analisis berbasis data yang membantu Anda menemukan kota dan kabupaten paling prospektif untuk usaha, properti, dan investasi.</p>
          <div className="btn-group">
            <Link to="/dashboard" className="btn btn-primary">Lihat Dashboard</Link>
            <Link to="/map" className="btn btn-outline">Jelajahi Peta</Link>
          </div>
          <div className="hero-stats">
            <div className="hero-stat"><div className="hero-stat-value">119</div><div className="hero-stat-label">Kota & Kabupaten</div></div>
            <div className="hero-stat"><div className="hero-stat-value">6</div><div className="hero-stat-label">Provinsi</div></div>
            <div className="hero-stat"><div className="hero-stat-value">4</div><div className="hero-stat-label">Kategori Skor</div></div>
            <div className="hero-stat"><div className="hero-stat-value">50+</div><div className="hero-stat-label">Indikator Data</div></div>
          </div>
        </div>
      </section>

      <div className="container">
        <div style={{textAlign:'center',margin:'3rem 0 1rem'}}>
          <h2 style={{fontSize:'1.8rem',fontWeight:800}}>Analisis Komprehensif Berbasis Data</h2>
          <p style={{color:'#94a3b8',maxWidth:'600px',margin:'0.75rem auto 0'}}>Setiap keputusan investasi didukung oleh data demografi, ekonomi, infrastruktur, dan properti terkini.</p>
        </div>
        <div className="features-grid">
          <div className="feature-card animate-in animate-in-delay-1">
            <div className="feature-icon">&#x1F4CA;</div>
            <h3>Dashboard Interaktif</h3>
            <p>Lihat ranking seluruh wilayah dengan skor yang mudah dipahami, filter berdasarkan provinsi dan tujuan investasi.</p>
          </div>
          <div className="feature-card animate-in animate-in-delay-2">
            <div className="feature-icon">&#x1F5FA;&#xFE0F;</div>
            <h3>Peta Visual Potensi</h3>
            <p>Eksplorasi peta interaktif dengan heatmap warna berdasarkan skor potensi setiap wilayah di Pulau Jawa.</p>
          </div>
          <div className="feature-card animate-in animate-in-delay-3">
            <div className="feature-icon">&#x1F916;</div>
            <h3>AI Insight</h3>
            <p>Dapatkan ringkasan cerdas tentang kekuatan, risiko, dan rekomendasi setiap wilayah dari analisis AI.</p>
          </div>
          <div className="feature-card animate-in animate-in-delay-1">
            <div className="feature-icon">&#x1F4C8;</div>
            <h3>Skor Multi-Dimensi</h3>
            <p>Empat kategori skor: Potensi Usaha, Investasi Properti, Pertumbuhan Wilayah, dan Risiko Investasi.</p>
          </div>
          <div className="feature-card animate-in animate-in-delay-2">
            <div className="feature-icon">&#x2696;&#xFE0F;</div>
            <h3>Perbandingan Wilayah</h3>
            <p>Bandingkan hingga 4 wilayah sekaligus dengan radar chart dan tabel detail untuk analisis mendalam.</p>
          </div>
          <div className="feature-card animate-in animate-in-delay-3">
            <div className="feature-icon">&#x1F3AF;</div>
            <h3>Rekomendasi Cerdas</h3>
            <p>Pilih tujuan investasi Anda dan dapatkan 5 wilayah terbaik yang paling sesuai dengan kebutuhan.</p>
          </div>
        </div>

        <div style={{textAlign:'center',margin:'3rem 0'}}>
          <Link to="/dashboard" className="btn btn-primary" style={{fontSize:'1rem',padding:'14px 36px'}}>Mulai Analisis Sekarang</Link>
        </div>
      </div>
    </div>
  );
}
