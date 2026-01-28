import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { ChartDataItem } from "../types";
import { SEVERITY_COLORS } from "./chartHelpers";

interface PieChartProps {
  chartData: ChartDataItem[];
}

const PieChartComponent: React.FC<PieChartProps> = ({ chartData }) => {
  // Explicitly mapping names to ensure the Red color is used for Fraud
  const getColor = (name: string) => {
    if (name === "Fraud") return SEVERITY_COLORS.FRAUD;
    return SEVERITY_COLORS.NORMAL;
  };

  return (
    <div className="w-full h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            innerRadius={65}
            outerRadius={85}
            paddingAngle={5}
            dataKey="value"
            animationDuration={1000}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getColor(entry.name)}
                stroke="none"
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid #e5e7eb",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            }}
          />
          <Legend verticalAlign="bottom" height={36} iconType="circle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PieChartComponent;
