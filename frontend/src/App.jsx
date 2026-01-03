import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import DashboardContent from "./components/DashboardContent";
import HistoryContent from "./components/HistoryContent";
import ReportsContent from "./components/ReportsContent";
import UploadCard from "./components/UploadCard";

export default function App() {
  const [activeNav, setActiveNav] = useState("Dashboard");
  const [predictionData, setPredictionData] = useState(null);

  const handleUploadSuccess = (data) => {
    setPredictionData(data);
    setActiveNav("Dashboard");
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        backgroundColor: "#0d1117",
        color: "#c9d1d9",
      }}
    >
      <Sidebar activeNav={activeNav} setActiveNav={setActiveNav} />

      <div style={{ flex: 1, padding: "40px", overflowY: "auto" }}>
        {activeNav === "Dashboard" && (
          <>
            <UploadCard onUploadSuccess={handleUploadSuccess} />
            {predictionData ? (
              <DashboardContent data={predictionData} />
            ) : (
              <div
                style={{
                  textAlign: "center",
                  marginTop: "50px",
                  color: "#8b949e",
                }}
              >
                <h2>Ready for Analysis</h2>
                <p>
                  Upload a CSV file to detect Pump & Dump patterns using
                  Isolation Forest AI.
                </p>
              </div>
            )}
          </>
        )}

        {activeNav === "History" && <HistoryContent />}
        {activeNav === "Reports" && <ReportsContent />}
      </div>
    </div>
  );
}
