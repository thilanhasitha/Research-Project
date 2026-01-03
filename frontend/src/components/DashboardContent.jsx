import React, { useState } from "react";
import styled from "styled-components";
import StatBox from "./StatBox";
import LineChartComponent from "./LineChartComponent";
import PieChartComponent from "./PieChartComponent";

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 30px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  height: 400px;
`;

export default function DashboardContent({ data }) {
  // Mapping the JSON output to your Dashboard
  const anomalies = data.anomalies || [];

  const stats = {
    detectedAnomalies: { value: data.anomaly_count, change: "Identified" },
    highRisk: {
      value: anomalies.filter((a) => a.anomaly_score > 0.65).length,
      change: "Critical",
    },
    totalRows: { value: data.total_rows, change: "Scanned" },
    companies: {
      value: [...new Set(anomalies.map((a) => a.Company))].length,
      change: "Analyzed",
    },
  };

  // Convert JSON to Recharts format
  const lineData = anomalies.map((item) => ({
    name: item.Date,
    anomalies: item.anomaly_score,
  }));

  const pieData = [
    { name: "Fraud Candidates", value: data.anomaly_count },
    { name: "Normal Activity", value: data.total_rows - data.anomaly_count },
  ];

  return (
    <DashboardContainer>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h2 style={{ margin: 0 }}>
          Analysis Report: {data.task_id.split("-")[0]}
        </h2>
      </div>

      <StatsGrid>
        <StatBox
          label="Detected Anomalies"
          value={stats.detectedAnomalies.value}
          change={stats.detectedAnomalies.change}
        />
        <StatBox
          label="High Severity"
          value={stats.highRisk.value}
          change={stats.highRisk.change}
        />
        <StatBox
          label="Total Days"
          value={stats.totalRows.value}
          change={stats.totalRows.change}
        />
        <StatBox
          label="Companies"
          value={stats.companies.value}
          change={stats.companies.change}
        />
      </StatsGrid>

      <ChartsGrid>
        <LineChartComponent chartData={lineData} />
        <PieChartComponent chartData={pieData} />
      </ChartsGrid>

      {/* Visual Proof from Backend */}
      <div
        style={{
          background: "#161b22",
          padding: "20px",
          borderRadius: "8px",
          border: "1px solid #30363d",
        }}
      >
        <h3 style={{ marginBottom: "15px" }}>
          Spatial Isolation Proof (PCA Analysis)
        </h3>
        <img
          src={`http://127.0.0.1:8000${data.chart_urls[0]}`}
          alt="PCA Result"
          style={{ width: "100%", borderRadius: "4px" }}
        />
      </div>
    </DashboardContainer>
  );
}
