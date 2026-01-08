import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function RiskReturnChart({ data }) {
  if (!data || data.length === 0) return null;

  // Sort by volatility (safer → riskier)
  const sortedData = [...data].sort(
    (a, b) => a.volatility - b.volatility
  );

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={sortedData}
        layout="vertical"
        margin={{ left: 40 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="stock" type="category" />
        <Tooltip />
        <Bar
          dataKey="volatility"
          fill="#2563eb"
          name="Volatility"
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default RiskReturnChart;
