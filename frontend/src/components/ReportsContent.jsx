import React from "react";
import styled from "styled-components";
import {
  MdReport,
  MdDownload,
  MdPictureAsPdf,
  MdTextFormat,
} from "react-icons/md";
import jsPDF from "jspdf"; // Already installed

// Hardcoded Report Data (Simulating available reports)
const availableReports = [
  {
    id: "daily-q3-2025",
    name: "Daily Summary Q3 2025",
    date: "2025-11-10",
    type: "Daily",
    anomalies: "1,204",
    impact: "$1.5M",
    data: "dashboardStats",
  },
  {
    id: "weekly-oct-2025",
    name: "Weekly Anomalies October",
    date: "2025-11-03",
    type: "Weekly",
    anomalies: "850",
    impact: "$0.9M",
    data: "dashboardStats",
  },
  {
    id: "custom-q2-2025",
    name: "Custom Quarterly Report Q2",
    date: "2025-10-15",
    type: "Custom",
    anomalies: "2,100",
    impact: "$2.8M",
    data: "dashboardStats",
  },
];

// Re-using the hardcoded data structure from App.jsx for demonstration
const mockStats = {
  detectedAnomalies: { value: "1,204", change: "+5.2%" },
  highSeverityAlerts: { value: 89, change: "+12%" },
  uniqueFraudTypes: { value: 4, change: "-2.1%" },
  estimatedFinancialImpact: { value: "$1.5M", change: "+8%" },
};

// --- Styled Components ---

const ReportContainer = styled.div`
  padding: 20px 0;
`;

const SectionTitle = styled.h2`
  color: #c9d1d9;
  margin-bottom: 25px;
  font-size: 24px;
`;

const ReportList = styled.div`
  background-color: #161b22;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #30363d;
`;

const ReportItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #30363d;

  &:last-child {
    border-bottom: none;
  }
`;

const ReportInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const ReportName = styled.span`
  font-weight: 600;
  font-size: 16px;
  color: #58a6ff;
  margin-bottom: 4px;
`;

const ReportDetails = styled.span`
  font-size: 13px;
  color: #8b949e;
`;

const ActionGroup = styled.div`
  display: flex;
  gap: 10px;
`;

const ExportButton = styled.button`
  background-color: ${(props) => (props.primary ? "#3f9efc" : "#30363d")};
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-weight: 500;

  &:hover {
    background-color: ${(props) => (props.primary ? "#58a6ff" : "#444c56")};
  }

  svg {
    margin-right: 5px;
  }
`;

// --- PDF Generation Logic (Re-used) ---
const generatePDF = (reportName, stats) => {
  const doc = new jsPDF("p", "mm", "a4");
  let y = 15;

  // Header
  doc.setFontSize(22);
  doc.setTextColor(50, 50, 50);
  doc.text(`FraudGuard Report: ${reportName}`, 15, y);
  y += 10;

  doc.setFontSize(10);
  doc.setTextColor(150, 150, 150);
  doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 15, y);
  y += 15;

  // Key Statistics
  doc.setFontSize(16);
  doc.setTextColor(0, 0, 0);
  doc.text("Key Performance Indicators", 15, y);
  y += 8;

  doc.setFontSize(12);
  doc.setTextColor(50, 50, 50);

  const statKeys = Object.keys(stats);
  statKeys.forEach((key) => {
    const label = key.replace(/([A-Z])/g, " $1").trim();
    const stat = stats[key];

    doc.text(`${label}: ${stat.value}`, 15, y);
    doc.text(`Change: ${stat.change}`, 80, y);
    y += 7;
  });

  // Save
  doc.save(`${reportName.replace(/\s/g, "_")}_Report.pdf`);
};

// --- Component ---
export default function ReportsContent() {
  const handleExport = (report, format) => {
    // In a real app, you would fetch specific report data here based on report.id
    const reportData = mockStats;

    if (format === "pdf") {
      generatePDF(report.name, reportData);
    } else if (format === "word") {
      // Word export is complex, often done by generating HTML/RTF, but we'll simulate a download:
      alert(`Simulating download for ${report.name} as Word (DOCX).`);
    }
  };

  return (
    <ReportContainer>
      <SectionTitle>
        <MdReport style={{ verticalAlign: "middle", marginRight: "10px" }} />{" "}
        Available Reports
      </SectionTitle>

      <ReportList>
        {availableReports.map((report) => (
          <ReportItem key={report.id}>
            <ReportInfo>
              <ReportName>{report.name}</ReportName>
              <ReportDetails>
                {report.type} | Generated: {report.date} | Anomalies:{" "}
                {report.anomalies} | Impact: {report.impact}
              </ReportDetails>
            </ReportInfo>
            <ActionGroup>
              <ExportButton
                primary
                onClick={() => handleExport(report, "pdf")}
                title="Export as PDF"
              >
                <MdPictureAsPdf size={16} /> PDF
              </ExportButton>
              <ExportButton
                onClick={() => handleExport(report, "word")}
                title="Export as Word (Simulated)"
              >
                <MdTextFormat size={16} /> DOCX
              </ExportButton>
            </ActionGroup>
          </ReportItem>
        ))}
      </ReportList>
    </ReportContainer>
  );
}
