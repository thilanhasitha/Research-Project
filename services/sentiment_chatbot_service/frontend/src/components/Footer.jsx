import React from 'react';
import { Link } from 'react-router-dom';
import { Instagram } from 'lucide-react';
import Newsletter from './NewsLetter';

const Footer = () => {
  const menuLinks = [
    { name: 'Home', path: '/' },
    { name: 'Explainableai', path: '/explainableai' },
    { name: 'Fraude', path: '/fraude' },
    { name: 'Portfolio', path: '/portfolio' },
  ];
    
  const supportLinks = [
    { name: 'Help', path: '/help' },
    { name: 'Returns & Exchanges', path: '/help' },
    { name: 'Trading policy', path: '/help' }
  ];

  return (
    <footer className="bg-gray-800 border-t border-purple-500">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Menu */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-white">Menu</h3>
            <ul className="space-y-2">
              {menuLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-lg font-semibold mb-4 text-white">Support</h3>
            <ul className="space-y-2">
              {supportLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>


          {/* Newsletter */}
          <Newsletter />
        </div>

        {/* Bottom Footer */}
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-400 text-sm">
            <p>Copyright © 2025, Stock Market Analyzer.</p>
            <p>Designed & Developed by RP-356 Group</p>
          </div>
          <div className="mt-4 md:mt-0">
            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <Instagram className="h-6 w-6 cursor-pointer" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;