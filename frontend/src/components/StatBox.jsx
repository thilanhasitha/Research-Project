import React from "react";
import styled from "styled-components";

// --- Styled Components ---
const StatCard = styled.div`
  background-color: #161b22;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #30363d;
`;

const StatLabel = styled.p`
  color: #8b949e;
  margin: 0 0 10px 0;
  font-size: 14px;
`;

const StatValue = styled.p`
  font-size: 32px;
  font-weight: bold;
  margin: 0;
`;

const StatChange = styled.span`
  font-size: 14px;
  font-weight: 500;
  color: ${(props) =>
    props.isNegative ? "#f85149" : "#2ea043"}; /* Red or Green */
`;

// --- Component ---
export default function StatBox({ label, value, change }) {
  const isNegative = change.startsWith("-");
  return (
    <StatCard>
      <StatLabel>{label}</StatLabel>
      <StatValue>{value}</StatValue>
      <StatChange isNegative={isNegative}>{change}</StatChange>
    </StatCard>
  );
}
