import React, { useState } from "react";
import styled from "styled-components";
import UploadCard from "./UploadCard";
import StatBox from "./StatBox";
import LineChartComponent from "./LineChartComponent";
import PieChartComponent from "./PieChartComponent";
import jsPDF from "jspdf";
import { MdPictureAsPdf, MdTextFormat } from "react-icons/md";

// --- Styled Components ---

const ReportHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ReportTitle = styled.h2`
  color: #c9d1d9;
  margin: 0;
  font-size: 24px;
`;

const TabBar = styled.div`
  display: flex;
  margin-bottom: 20px;
`;

const Tab = styled.div`
  padding: 10px 15px;
  cursor: pointer;
  color: ${(props) => (props.active ? "#58a6ff" : "#8b949e")};
  border-bottom: 2px solid
    ${(props) => (props.active ? "#58a6ff" : "transparent")};
  font-weight: 500;
  margin-right: 20px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 40px;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  height: 400px;
`;

const ExportButton = styled.button`
  background-color: ${(props) =>
    props.word ? "#1E6EAE" : "#3f9efc"}; /* Word-blue or primary blue */
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-weight: 600;

  &:hover {
    background-color: ${(props) => (props.word ? "#2a87c0" : "#58a6ff")};
  }

  svg {
    margin-right: 5px;
  }
`;

// --- Component ---
export default function DashboardContent({ data }) {
  const [activeTab, setActiveTab] = useState("Daily Reports");
  const stats = data.dashboardStats;

  // Function to generate PDF report using jspdf
  const generatePDFReport = () => {
    const doc = new jsPDF("p", "mm", "a4");
    let y = 15;

    // Header, Stats, and Summary logic (omitted for brevity, see previous response)
    // ... (This function remains the same as provided earlier) ...

    // Example of adding text:
    doc.setFontSize(22);
    doc.text("FraudGuard Generated Report", 15, y);
    y += 25;

    doc.setFontSize(16);
    doc.text("Key Performance Indicators", 15, y);
    y += 8;

    const statKeys = Object.keys(stats);
    statKeys.forEach((key) => {
      const label = key.replace(/([A-Z])/g, " $1").trim();
      const stat = stats[key];
      doc.setFontSize(12);
      doc.text(`${label}: ${stat.value}`, 15, y);
      doc.text(`Change: ${stat.change}`, 80, y);
      y += 7;
    });

    doc.save(
      `FraudGuard_Dashboard_Report_${activeTab.replace(/\s/g, "_")}.pdf`
    );
  };

  // Function to simulate Word report using HTML to .doc conversion
  const generateWordReport = () => {
    const reportName = `FraudGuard_Dashboard_Report_${activeTab.replace(
      /\s/g,
      "_"
    )}`;

    // 1. Build the HTML content for the report
    let htmlContent = `
        <html>
            <head>
                <meta charset="utf-8">
                <title>${reportName}</title>
            </head>
            <body>
                <h1>FraudGuard Generated Report: ${activeTab}</h1>
                <h2>Key Performance Indicators</h2>
                <table border="1" cellpadding="10" cellspacing="0" style="width: 50%;">
                    <thead><tr style="background-color: #f2f2f2;"><th>Metric</th><th>Value</th><th>Change</th></tr></thead>
                    <tbody>
                        <tr><td>Detected Anomalies</td><td>${stats.detectedAnomalies.value}</td><td>${stats.detectedAnomalies.change}</td></tr>
                        <tr><td>High-Severity Alerts</td><td>${stats.highSeverityAlerts.value}</td><td>${stats.highSeverityAlerts.change}</td></tr>
                        <tr><td>Unique Fraud Types</td><td>${stats.uniqueFraudTypes.value}</td><td>${stats.uniqueFraudTypes.change}</td></tr>
                        <tr><td>Estimated Financial Impact</td><td>${stats.estimatedFinancialImpact.value}</td><td>${stats.estimatedFinancialImpact.change}</td></tr>
                    </tbody>
                </table>
            </body>
        </html>
    `;

    // 2. Create a Blob and trigger the download as a .doc file
    const blob = new Blob(["\ufeff", htmlContent], {
      type: "application/msword",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${reportName}.doc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <UploadCard />

      <ReportHeader>
        <ReportTitle>Generated Report</ReportTitle>
        <div style={{ display: "flex", gap: "10px" }}>
          {" "}
          {/* Container for both buttons */}
          <ExportButton onClick={generatePDFReport} title="Export as PDF">
            <MdPictureAsPdf size={20} />
            Export PDF
          </ExportButton>
          <ExportButton
            word
            onClick={generateWordReport}
            title="Export as Word (.doc)"
          >
            <MdTextFormat size={20} />
            Export Word
          </ExportButton>
        </div>
      </ReportHeader>

      <TabBar>
        {["Daily Reports", "Weekly Summaries", "Custom Reports"].map((tab) => (
          <Tab
            key={tab}
            active={activeTab === tab}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </Tab>
        ))}
      </TabBar>

      <StatsGrid>
        <StatBox
          label="Detected Anomalies"
          value={stats.detectedAnomalies.value}
          change={stats.detectedAnomalies.change}
        />
        <StatBox
          label="High-Severity Alerts"
          value={stats.highSeverityAlerts.value}
          change={stats.highSeverityAlerts.change}
        />
        <StatBox
          label="Unique Fraud Types"
          value={stats.uniqueFraudTypes.value}
          change={stats.uniqueFraudTypes.change}
        />
        <StatBox
          label="Estimated Financial Impact"
          value={stats.estimatedFinancialImpact.value}
          change={stats.estimatedFinancialImpact.change}
        />
      </StatsGrid>

      <ChartsGrid>
        <LineChartComponent chartData={data.lineChart} />
        <PieChartComponent chartData={data.pieChart} />
      </ChartsGrid>
    </>
  );
}
