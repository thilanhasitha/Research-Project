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

// --- Constants ---
const PIE_COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

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
export default function PieChartComponent({ chartData }) {
  return (
    <ChartCard>
      <ChartTitle>Anomalies by Fraud Type</ChartTitle>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={80}
            fill="#8884d8"
            labelLine={false}
            label={({ name, percent }) =>
              `${name} (${(percent * 100).toFixed(0)}%)`
            }
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={PIE_COLORS[index % PIE_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#161b22",
              border: "1px solid #30363d",
            }}
            labelStyle={{ color: "#c9d1d9" }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} iconSize={10} />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
