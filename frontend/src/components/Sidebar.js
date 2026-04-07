import React from 'react';
import {
  Home,
  Upload,
  Settings,
  Users,
  Menu,
  X,
} from 'lucide-react';
import '../styles/Sidebar.css';

function Sidebar({ isOpen, toggleSidebar, navigateTo, currentPage }) {
  const handleNavClick = (page, e) => {
    e.preventDefault();
    navigateTo(page);
  };

  return (
    <>
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>
      
      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="sidebar-logo">VC</div>
        </div>

        <nav className="sidebar-nav">
          <a href="#" onClick={(e) => handleNavClick('dashboard', e)} className={`nav-item ${currentPage === 'dashboard' ? 'active' : ''}`}>
            <Home size={20} />
            <span>Dashboard</span>
          </a>
          <a href="#" onClick={(e) => handleNavClick('upload', e)} className={`nav-item ${currentPage === 'upload' ? 'active' : ''}`}>
            <Upload size={20} />
            <span>Upload Video</span>
          </a>
          <a href="#" onClick={(e) => handleNavClick('settings', e)} className={`nav-item ${currentPage === 'settings' ? 'active' : ''}`}>
            <Settings size={20} />
            <span>Settings</span>
          </a>
          <a href="#" onClick={(e) => handleNavClick('account', e)} className={`nav-item ${currentPage === 'account' ? 'active' : ''}`}>
            <Users size={20} />
            <span>Account</span>
          </a>
        </nav>

        <div className="sidebar-footer">
          <button className="help-btn">?</button>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
