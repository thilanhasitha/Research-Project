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



export interface ForensicLSTMResponse {
  status: string;
  scan_summary: {
    total_rows_scanned: number;
    total_companies: number;
    high_risk_alerts_found: number;
    fraud_breakdown: Record<string, number>;
  };
  alerts: ForensicAlert[];
  visual_evidence_url: string;
}

export interface ForensicAlert {
  Symbol: string;
  Date: string;
  fraud_type: string;
  risk_level: string;
  forensic_evidence: string;
  confidence_score: string;
  dtw_score: number;
  Price_Impact: number;
  // ... other numeric fields from your JSON
}