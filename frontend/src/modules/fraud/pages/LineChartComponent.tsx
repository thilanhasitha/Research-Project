import React from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { TimelineDataItem } from "../types";
import { SEVERITY_COLORS } from "./chartHelpers";

interface Props {
  chartData: TimelineDataItem[];
}

const LineChartComponent: React.FC<Props> = ({ chartData }) => {
  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#30363d" />
          <XAxis dataKey="name" hide />
          <YAxis domain={[0, 1]} tick={{fontSize: 12}} />
          <Tooltip 
            contentStyle={{ backgroundColor: "#161b22", border: "1px solid #30363d" }}
          />
          <Area
            type="monotone"
            dataKey="anomalies"
            stroke={SEVERITY_COLORS.PRIMARY}
            fill={SEVERITY_COLORS.PRIMARY}
            fillOpacity={0.1}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LineChartComponent;