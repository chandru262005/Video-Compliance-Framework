import React from 'react';
import { Search, Edit, Bell, User } from 'lucide-react';
import '../styles/Header.css';

function Header() {
  return (
    <header className="app-header">
      <div className="header-left">
        <h1 className="header-title">Cloud Compliance Dashboard</h1>
      </div>

      <div className="header-search">
        <input
          type="text"
          placeholder="Search resources..."
          className="search-input"
        />
        <Search size={18} className="search-icon" />
      </div>

      <div className="header-actions">
        <button className="header-btn" title="Edit">
          <Edit size={18} />
        </button>
        <button className="header-btn" title="Notifications">
          <Bell size={18} />
        </button>
        <button className="header-btn" title="Profile">
          <User size={18} />
        </button>
      </div>
    </header>
  );
}

export default Header;
