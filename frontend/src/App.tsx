import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Chatbot from './components/Chatbot';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import MapExplorer from './pages/MapExplorer';
import RegionDetail from './pages/RegionDetail';
import Comparison from './pages/Comparison';
import Recommendation from './pages/Recommendation';

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/map" element={<MapExplorer />} />
        <Route path="/region/:id" element={<RegionDetail />} />
        <Route path="/compare" element={<Comparison />} />
        <Route path="/recommendations" element={<Recommendation />} />
      </Routes>
      <Footer />
      <Chatbot />
    </>
  );
}

