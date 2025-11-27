import React from "react";
import styled from "styled-components";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// --- Styled Components ---
const ChartCard = styled.div`
  background-color: #161b22;
  border-radius: 8px;
  border: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  padding: 20px;
  height: 100%;
`;

const ChartTitle = styled.h3`
  color: #c9d1d9;
  font-size: 18px;
  margin-bottom: 15px;
  font-weight: 500;
`;

// --- Component ---
export default function LineChartComponent({ chartData }) {
  return (
    <ChartCard>
      <ChartTitle>Anomalous Activity Over Time</ChartTitle>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
          <XAxis dataKey="name" stroke="#8b949e" />
          <YAxis stroke="#8b949e" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#161b22",
              border: "1px solid #30363d",
            }}
            labelStyle={{ color: "#c9d1d9" }}
          />
          <Line
            type="monotone"
            dataKey="anomalies"
            stroke="#58a6ff"
            strokeWidth={3}
            dot={false}
            name="Anomalies"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
