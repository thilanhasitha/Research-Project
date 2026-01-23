import Card from '../../../shared/components/Card';

const About = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">About StockSense</h1>
        
        <Card className="mb-6">
          <p className="text-gray-700 mb-4">
            StockSense is an advanced stock market decision support system that leverages 
            artificial intelligence, machine learning, and comprehensive data analysis to 
            help investors make informed decisions.
          </p>
          <p className="text-gray-700">
            Our platform integrates multiple specialized microservices to provide a holistic 
            view of the stock market, combining fundamental analysis, sentiment tracking, 
            fraud detection, and personalized recommendations.
          </p>
        </Card>

        <h2 className="text-2xl font-bold text-gray-900 mb-4">Our Services</h2>

        <div className="space-y-4">
          <Card>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Valuation Service</h3>
            <p className="text-gray-700">
              Uses Discounted Cash Flow (DCF) models to calculate the intrinsic value of stocks 
              based on financial data. Helps identify undervalued and overvalued opportunities.
            </p>
          </Card>

          <Card>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Sentiment Analysis</h3>
            <p className="text-gray-700">
              Analyzes market sentiment from news articles, social media, and financial reports. 
              Includes an AI-powered chatbot to answer your questions about specific stocks.
            </p>
          </Card>

          <Card>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Fraud Detection</h3>
            <p className="text-gray-700">
              Monitors trading patterns in real-time to detect suspicious activities, price 
              manipulation, and unusual trading behaviors that may indicate fraud.
            </p>
          </Card>

          <Card>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Recommendations</h3>
            <p className="text-gray-700">
              Provides personalized stock recommendations based on your risk tolerance, 
              investment horizon, and preferences, combining insights from all other services.
            </p>
          </Card>
        </div>

        <Card className="mt-8 bg-primary-50">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Our Mission</h3>
          <p className="text-gray-700">
            To democratize access to sophisticated investment analysis tools and empower 
            investors of all levels to make confident, data-driven decisions.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default About;
