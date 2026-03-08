import {
  AnomalyData,
  PredictionResponse,
  ChartDataItem,
  TimelineDataItem,
} from "../types";

export const transformLineData = (
  detections: AnomalyData[],
): TimelineDataItem[] => {
  if (!detections || !Array.isArray(detections)) return [];
  return detections.map((item) => ({
    name: item.date,
    anomalies: item.anomaly_score,
  }));
};

export const transformPieData = (data: PredictionResponse): ChartDataItem[] => {
  const fraudCount = data.scan_summary?.frauds_detected || 0;
  const total = data.scan_summary?.total_rows_processed || 0;

  return [
    { name: "Fraud", value: fraudCount },
    { name: "Normal", value: total - fraudCount },
  ];
};

export const SEVERITY_COLORS = {
  FRAUD: "#ef4444",
  NORMAL: "#22c55e",
  PRIMARY: "#3b82f6",
};

export const transformForensicPieData = (
  breakdown: Record<string, number>,
): ChartDataItem[] => {
  return Object.entries(breakdown).map(([name, value]) => ({
    name,
    value,
  }));
};

// Add to your SEVERITY_COLORS
export const FORENSIC_COLORS: Record<string, string> = {
  "BOT SIGNATURE": "#8b5cf6", // Purple
  "MARKET RAMPING": "#f59e0b", // Amber
  "CRITICAL: PUMP & DUMP": "#ef4444", // Red
};