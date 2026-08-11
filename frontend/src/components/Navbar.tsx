import { NavLink } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand"><span>Prospek</span>Jawa</NavLink>
      <div className="navbar-links">
        <NavLink to="/dashboard" className={({isActive})=>isActive?'active':''}>Dashboard</NavLink>
        <NavLink to="/map" className={({isActive})=>isActive?'active':''}>Peta</NavLink>
        <NavLink to="/recommendations" className={({isActive})=>isActive?'active':''}>Rekomendasi</NavLink>
        <NavLink to="/compare" className={({isActive})=>isActive?'active':''}>Bandingkan</NavLink>
      </div>
    </nav>
  );
}
