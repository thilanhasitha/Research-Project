import { useLocation } from "react-router-dom";
import RiskReturnChart from "../components/RiskReturnChart";

function Recommendations() {
  const { state } = useLocation();

  if (!state) return <p>No recommendations found</p>;

  const { risk_level, recommendations = [] } = state;

  const riskClass =
    risk_level === "Low"
      ? "low"
      : risk_level === "Medium"
      ? "medium"
      : "high";

  return (
    <div className="container">
      <div className="card">

        {/* HEADER */}
        <h2>
          Recommended Stocks{" "}
          <span className={`risk-tag ${riskClass}`}>
            {risk_level} Risk
          </span>
        </h2>

        <p className="helper-text">
          These stocks align with your risk profile based on historical volatility
          and return patterns.
        </p>

        {/* TABLE */}
        <div className="stock-table">
          <table>
            <thead>
              <tr>
                <th>Stock Code</th>
                <th>Company</th>
                <th>Risk</th>
                <th>Volatility</th>
                <th>Mean Return</th>
              </tr>
            </thead>
            <tbody>
              {recommendations.length > 0 ? (
                recommendations.map((s, index) => (
                  <tr key={index}>
                    <td><b>{s.stock}</b></td>
                    <td>{s.company_name}</td>
                    <td>
                      <span className={`risk-tag ${riskClass}`}>
                        {s.predicted_risk}
                      </span>
                    </td>
                    <td>{s.volatility?.toFixed(4)}</td>
                    <td>{s.mean_return?.toFixed(4)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" align="center">
                    No recommendations available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* WHY THESE STOCKS */}
        <div className="section-header">Why these stocks?</div>
        {recommendations.map((s, index) => (
          <div key={index} className="stock-reason">
            <b>{s.stock}</b> – {s.reason}
          </div>
        ))}

        {/* CHART */}
        <div className="section-header">
          Risk vs Return Analysis
        </div>
        <div className="chart-card">
          <RiskReturnChart data={recommendations} />
        </div>

      </div>
    </div>
  );
}

export default Recommendations;
