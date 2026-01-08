import { useLocation, useNavigate } from "react-router-dom";

function RiskResult() {
  const { state } = useLocation();
  const navigate = useNavigate();

  if (!state) return <p>No data found</p>;

  const { risk_level, explanation = [], recommendations = [] } = state;

  const badgeClass =
    risk_level === "Low"
      ? "risk-low"
      : risk_level === "Medium"
      ? "risk-medium"
      : "risk-high";

  const summaryText =
    risk_level === "Low"
      ? "You have a conservative financial profile with lower exposure to risk."
      : risk_level === "Medium"
      ? "You have a balanced financial profile with moderate risk exposure."
      : "You have a higher risk profile with greater financial exposure.";

  return (
    <div className="container">
      <div className="card">

        {/* HEADER */}
        <div className="risk-header">
          <h2>Predicted Risk Level</h2>
          <span className={`risk-badge ${badgeClass}`}>
            {risk_level}
          </span>
        </div>

        {/* SUMMARY */}
        <p className="risk-summary">{summaryText}</p>

        <h3>Why this risk?</h3>

        {explanation.length > 0 ? (
          explanation.map((text, index) => (
            <div key={index} className="explain-card">
              <div className="explain-icon">📊</div>
              <div>{text}</div>
            </div>
          ))
        ) : (
          <p>No explanation available.</p>
        )}

        {/* CTA */}
        <div className="cta">
          <button
            onClick={() =>
              navigate("/recommendations", {
                state: {
                  risk_level,
                  recommendations,
                  explanation,
                },
              })
            }
          >
            Get Stock Recommendations →
          </button>
        </div>
      </div>
    </div>
  );
}

export default RiskResult;
