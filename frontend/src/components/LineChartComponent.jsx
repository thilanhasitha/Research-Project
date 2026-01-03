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
  Area,
  AreaChart,
} from "recharts";

const ChartCard = styled.div`
  background-color: #161b22;
  border-radius: 12px;
  border: 1px solid #30363d;
  padding: 20px;
  height: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
`;

const ChartTitle = styled.h3`
  color: #58a6ff;
  font-size: 18px;
  margin-bottom: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
`;

export default function LineChartComponent({ chartData }) {
  return (
    <ChartCard>
      <ChartTitle>Detection Confidence Over Time</ChartTitle>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#58a6ff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#58a6ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#30363d"
            vertical={false}
          />
          <XAxis
            dataKey="name"
            stroke="#8b949e"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#8b949e"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            domain={[0, 1]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#0d1117",
              border: "1px solid #58a6ff",
              borderRadius: "8px",
              color: "#c9d1d9",
            }}
          />
          <Area
            type="monotone"
            dataKey="anomalies"
            stroke="#58a6ff"
            strokeWidth={3}
            fillOpacity={1}
            fill="url(#colorScore)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
