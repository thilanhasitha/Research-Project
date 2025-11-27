import React, { useState } from "react";
import styled, { createGlobalStyle } from "styled-components";
import { MdNotifications, MdAccountCircle } from "react-icons/md";
import Sidebar from "./components/Sidebar";
import DashboardContent from "./components/DashboardContent";
import HistoryContent from "./components/HistoryContent";
import ReportsContent from "./components/ReportsContent";

// --- Hardcoded Data (Keep in App or move to a separate 'data.js' for larger apps) ---
const hardcodedData = {
  dashboardStats: {
    detectedAnomalies: { value: "1,204", change: "+5.2%" },
    highSeverityAlerts: { value: 89, change: "+12%" },
    uniqueFraudTypes: { value: 4, change: "-2.1%" },
    estimatedFinancialImpact: { value: "$1.5M", change: "+8%" },
  },
  lineChart: [
    { name: "Mon", anomalies: 120, alerts: 5 },
    { name: "Tue", anomalies: 150, alerts: 8 },
    { name: "Wed", anomalies: 100, alerts: 3 },
    { name: "Thu", anomalies: 220, alerts: 10 },
    { name: "Fri", anomalies: 180, alerts: 7 },
    { name: "Sat", anomalies: 250, alerts: 12 },
    { name: "Sun", anomalies: 200, alerts: 9 },
  ],
  pieChart: [
    { name: "Account Takeover", value: 400 },
    { name: "Credit Card Fraud", value: 300 },
    { name: "Check Fraud", value: 300 },
    { name: "Application Fraud", value: 200 },
  ],
};

// --- Global Styles ---
const GlobalStyle = createGlobalStyle`
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
    background-color: #0d1117; /* Dark background */
    color: #c9d1d9; /* Light text */
    overflow-x: hidden;
  }
  * {
    box-sizing: border-box;
  }
`;

// --- Styled Components ---

// Main Layout
const Container = styled.div`
  display: flex;
  min-height: 100vh;
`;

// Main Content Wrapper
const MainContent = styled.main`
  flex-grow: 1;
  padding: 20px 30px;
`;

const Header = styled.header`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0 30px;
  border-bottom: 1px solid #30363d;
`;

const SearchBar = styled.div`
  flex-grow: 1;
  max-width: 600px;
  margin-right: 20px;

  input {
    width: 100%;
    padding: 10px 15px;
    border: 1px solid #30363d;
    background-color: #0d1117;
    color: #c9d1d9;
    border-radius: 6px;
    font-size: 16px;
  }
`;

const HeaderIcons = styled.div`
  display: flex;

  svg {
    margin-left: 20px;
    font-size: 24px;
    cursor: pointer;
    color: #c9d1d9;
  }
`;

export default function App() {
  const [activeNav, setActiveNav] = useState("Dashboard");

  return (
    <>
      <GlobalStyle />
      <Container>
        <Sidebar activeNav={activeNav} setActiveNav={setActiveNav} />

        <MainContent>
          <Header>
            <SearchBar>
              <input
                type="text"
                placeholder="Search by stock, date, or alert ID..."
              />
            </SearchBar>
            <HeaderIcons>
              <MdNotifications />
              <MdAccountCircle />
            </HeaderIcons>
          </Header>

          {/* Render content based on the active sidebar item */}
          {activeNav === "Dashboard" && (
            <DashboardContent data={hardcodedData} />
          )}
          {activeNav === "Reports" && <ReportsContent />}
          {activeNav === "Settings" && <h1>Settings Content Placeholder</h1>}
          {activeNav === "History" && <HistoryContent />}
        </MainContent>
      </Container>
    </>
  );
}
