import React from "react";
import styled from "styled-components";
import {
  PieChart,
  Pie,
  Cell,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// High-contrast palette: Emerald for Normal, Ruby for Fraud
const COLORS = ["#f85149", "#2ea043"];

const ChartCard = styled.div`
  background-color: #161b22;
  border-radius: 12px;
  border: 1px solid #30363d;
  padding: 20px;
  height: 100%;
`;

const ChartTitle = styled.h3`
  color: #c9d1d9;
  font-size: 18px;
  margin-bottom: 15px;
  font-weight: 500;
`;

export default function PieChartComponent({ chartData }) {
  return (
    <ChartCard>
      <ChartTitle>Data Composition</ChartTitle>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60} // Makes it a donut chart
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
                stroke="none"
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              backgroundColor: "#0d1117",
              border: "1px solid #30363d",
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value) => (
              <span style={{ color: "#c9d1d9", fontSize: "14px" }}>
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
