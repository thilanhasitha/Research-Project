import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/" className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">StockSense</span>
            </Link>
            <div className="hidden md:ml-10 md:flex md:space-x-8">
              <Link
                to="/"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-primary-600 transition-colors"
              >
                Home
              </Link>
              <Link
                to="/valuation"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
              >
                Valuation
              </Link>
              <Link
                to="/sentiment"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
              >
                Sentiment
              </Link>
              <Link
                to="/fraud-detection"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
              >
                Fraud Detection
              </Link>
              <Link
                to="/recommendations"
                className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
              >
                Recommendations
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Link
              to="/about"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              About
            </Link>
            <Link
              to="/contact"
              className="text-sm font-medium text-gray-700 hover:text-primary-600 transition-colors"
            >
              Contact
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
