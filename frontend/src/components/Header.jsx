import React, { useState, useContext, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Search, Menu, X } from "lucide-react";
import { NAV_ITEMS, ROUTES } from "../router/routes/routeConfig";


const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const profileMenuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
    };

    if (showProfileMenu) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showProfileMenu]);



  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-gray-900 text-white sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-2 sm:px-4 md:px-6 py-3 md:py-4">
        {/* Left Section */}
        <div className="flex items-center space-x-2 lg:space-x-4 flex-shrink-0">
          {/* Brand */}
          <Link
            to={ROUTES.HOME}
            className="text-2xl font-bold text-white hover:text-gray-300 transition-colors"
          >
            Stock Market Analyzer
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex space-x-4 lg:space-x-6 flex-shrink">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`transition-colors ${
                  isActive(item.path)
                    ? "text-purple-400 font-medium"
                    : "text-white hover:text-gray-300"
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-2 lg:space-x-4 flex-shrink-0">
          {/* Search (Desktop only) */}
          <div className="hidden lg:block relative flex-shrink">
            <input
              type="text"
              placeholder="What are you looking for?"
              className="bg-gray-700 rounded-full px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-gray-400 w-40 sm:w-48 md:w-56 lg:w-64 transition-all duration-300"
            />
            <Search className="absolute right-3 top-2.5 h-4 w-4 text-gray-400" />
          </div>

          

          {/* Hamburger Menu (Mobile only) */}
          <button
            className="lg:hidden focus:outline-none"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      
    </header>
  );
};

export default Header;