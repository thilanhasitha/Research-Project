import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";

function Home() {
  return (
    <div className="container">
      {/* HERO SECTION */}
      <div className="hero">
        <div className="hero-text">
          <h1>
            Intelligent Stock Recommendations,
            <br />
            <span>Explained Clearly.</span>
          </h1>

          <p>
            Analyze your investment risk profile using machine learning and
            understand <b>why</b> each recommendation is made with
            Explainable AI.
          </p>

          <Link to="/questionnaire">
            <button className="primary-btn">
              Start Risk Analysis →
            </button>
          </Link>
        </div>

        <div className="hero-image">
          <img src={heroImage} alt="AI Stock Analysis" />
        </div>
      </div>

      {/* FEATURES */}
      <h2 className="section-title">Why Choose This System?</h2>

      <div className="feature-grid">
        <div className="feature-card">
          <span>📊</span>
          <h4>Personalized Risk Analysis</h4>
          <p>
            Tailors recommendations based on your financial profile.
          </p>
        </div>

        <div className="feature-card">
          <span>🧠</span>
          <h4>Explainable AI</h4>
          <p>
            Transparent explanations for every prediction and recommendation.
          </p>
        </div>

        <div className="feature-card">
          <span>🔒</span>
          <h4>Reliable & Secure</h4>
          <p>
            Uses historical market data from the Colombo Stock Exchange.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Home;
