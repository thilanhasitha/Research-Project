import { Routes, Route } from "react-router-dom";
import Layout from "../app/Layout";

// Core pages
import Home from "../modules/core/pages/Home";
import About from "../modules/core/pages/About";
import Contact from "../modules/core/pages/Contact";
import NotFound from "../modules/core/pages/NotFound";

// Valuation Service
import ValuationDashboard from "../modules/valuation/pages/ValuationDashboard";

// Sentiment Chatbot
import SentimentDashboard from "../modules/sentiment/pages/SentimentDashboard";

// Fraud Detection
import FraudDashboard from "../modules/fraud/pages/FraudDashboard";

// Recommendations
import RecommendationDashboard from "../modules/recommendation/pages/RecommendationDashboard";

const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        <Route path="/valuation" element={<ValuationDashboard />} />
        <Route path="/sentiment" element={<SentimentDashboard />} />
        <Route path="/fraud-detection" element={<FraudDashboard />} />
        <Route path="/recommendations" element={<RecommendationDashboard />} />

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
