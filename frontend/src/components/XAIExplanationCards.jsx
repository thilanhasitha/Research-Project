const impactColors = {
  High: "#dc2626",
  Medium: "#f59e0b",
  Low: "#16a34a",
};

const XAIExplanationCards = ({ explanations = [] }) => {
  if (!explanations.length) {
    return <p>No explanation available.</p>;
  }

  return (
    <div style={{ marginTop: "30px" }}>
      <h3>Why this risk level?</h3>

      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
        {explanations.map((exp, index) => (
          <div
            key={index}
            style={{
              border: "1px solid #ddd",
              borderLeft: `6px solid ${impactColors[exp.impact]}`,
              borderRadius: "8px",
              padding: "16px",
              width: "280px",
              background: "#fafafa",
            }}
          >
            <h4>{exp.feature}</h4>
            <p>
              <b>Impact:</b>{" "}
              <span style={{ color: impactColors[exp.impact] }}>
                {exp.impact}
              </span>
            </p>
            <p>
              <b>Direction:</b>{" "}
              {exp.direction === "increase"
                ? "↑ Increases Risk"
                : "↓ Reduces Risk"}
            </p>
            <p style={{ fontSize: "14px", color: "#555" }}>
              {exp.message}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default XAIExplanationCards;
