export interface AnomalyData {
  ticker: string; // Backend: "ticker"
  date: string; // Backend: "date"
  anomaly_score: number; // Backend: "anomaly_score"
  pump_intensity: string;
  volume_surge: string;
  reason: string;
}

export interface PredictionResponse {
  status: string;
  scan_summary: {
    total_rows_processed: number;
    total_companies_scanned: number;
    frauds_detected: number;
    unique_companies_flagged: number;
    high_risk_alerts_found?: number;
    total_companies?: number;
  };
  detections: AnomalyData[]; // Backend: "detections"
  report_url?: string; // For M1 image
  visual_evidence_url?: string; // For M2 image
}


// Interface for History
export interface HistoryItem {
  task_id: string;
  timestamp: string;
  model_type: 'Pump & Dump' | 'Forensic LSTM';
  anomaly_count: number;
  total_rows: number;
  detections: AnomalyData[]; // We store the full results here for JSON export
}