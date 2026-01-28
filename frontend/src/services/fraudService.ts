import { fraudApi } from "./api";
import { PredictionResponse, HistoryItem } from "../modules/fraud/types";
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
// --- STATIC MOCK DATA ---
// src/services/fraudService.ts

const MOCK_HISTORY: any[] = [
  {
    status: "Success",
    task_id: "TASK-1769543800",
    timestamp: "2026-01-28 00:15:22",
    model_type: "Pump & Dump",
    scan_summary: {
      total_rows_processed: 8000,
      total_companies_scanned: 37,
      frauds_detected: 11,
      unique_companies_flagged: 8
    },
    detections: [
      { ticker: "ABANS FINANCIAL", date: "2023-07-19 00:00:00", pump_intensity: "17.9%", anomaly_score: 0.6976, volume_surge: "10.3x", reason: "Abnormal volume spike." },
      { ticker: "ALPHA FIRE", date: "2023-11-29 00:00:00", pump_intensity: "23.3%", anomaly_score: 0.6611, volume_surge: "7.2x", reason: "Abnormal volume spike." },
      { ticker: "AMANA LIFE", date: "2023-07-10 00:00:00", pump_intensity: "16.4%", anomaly_score: 0.7285, volume_surge: "15.8x", reason: "Abnormal volume spike." },
      { ticker: "AMF CO LTD", date: "2023-07-19 00:00:00", pump_intensity: "20.5%", anomaly_score: 0.7362, volume_surge: "16.6x", reason: "Abnormal volume spike." },
      { ticker: "AMF CO LTD", date: "2023-08-18 00:00:00", pump_intensity: "21.3%", anomaly_score: 0.6694, volume_surge: "8.5x", reason: "Abnormal volume spike." },
      { ticker: "ASIA CAPITAL", date: "2023-06-12 00:00:00", pump_intensity: "17.1%", anomaly_score: 0.6542, volume_surge: "7.5x", reason: "Abnormal volume spike." },
      { ticker: "AUTODROME", date: "2023-11-27 00:00:00", pump_intensity: "23.9%", anomaly_score: 0.7048, volume_surge: "10.2x", reason: "Abnormal volume spike." },
      { ticker: "BERUWALA RESORTS", date: "2023-02-16 00:00:00", pump_intensity: "16.7%", anomaly_score: 0.7088, volume_surge: "11.9x", reason: "Abnormal volume spike." },
      { ticker: "BERUWALA RESORTS", date: "2023-07-06 00:00:00", pump_intensity: "15.4%", anomaly_score: 0.6897, volume_surge: "10.2x", reason: "Abnormal volume spike." },
      { ticker: "BERUWALA RESORTS", date: "2023-12-04 00:00:00", pump_intensity: "20.0%", anomaly_score: 0.6842, volume_surge: "9.3x", reason: "Abnormal volume spike." },
      { ticker: "BLUE DIAMONDS", date: "2023-06-13 00:00:00", pump_intensity: "33.3%", anomaly_score: 0.741, volume_surge: "15.5x", reason: "Abnormal volume spike." }
    ],
    report_url: "/static/reports/fraud_report_1769543800.png"
  }
];

export const fraudService = {


  uploadPumpDump: async (file: File): Promise<PredictionResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fraudApi.post<PredictionResponse>(
      "/detect/pump-dump", // Base URL in api.ts should handle /api/v1
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return response.data; // Return direct data if backend isn't wrapped in extra "data" key
  },

  uploadForensicLSTM: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fraudApi.post<any>(
      "/detect/forensic-lstm",
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return response.data;
  },





   // GET STATIC HISTORY
  getHistory: async (): Promise<HistoryItem[]> => {
    // Simulating a delay like a real API
    return new Promise((resolve) => {
      setTimeout(() => resolve(MOCK_HISTORY), 800);
    });
  },




  downloadPDF: (item: any) => {
    const doc = new jsPDF();

    // 1. Add Header
    doc.setFontSize(18);
    doc.text("CSE Forensic Analysis Report", 14, 22);
    
    // 2. Add Metadata
    doc.setFontSize(11);
    doc.setTextColor(100);
    doc.text(`Task ID: ${item.task_id}`, 14, 32);
    doc.text(`Timestamp: ${item.timestamp}`, 14, 38);
    doc.text(`Model: ${item.model_type}`, 14, 44);

    // 3. Add Summary Statistics
    doc.setFontSize(14);
    doc.setTextColor(0);
    doc.text("Scan Summary", 14, 55);
    
    const summary = item.scan_summary;
    autoTable(doc, {
      startY: 60,
      head: [["Metric", "Value"]],
      body: [
        ["Total Rows Processed", summary?.total_rows_processed?.toLocaleString() || "N/A"],
        ["Companies Scanned", summary?.total_companies_scanned || "N/A"],
        ["Frauds Detected", summary?.frauds_detected || "N/A"],
        ["Unique Companies Flagged", summary?.unique_companies_flagged || "N/A"],
      ],
      theme: 'striped'
    });

    // 4. Add Detections Table (If data exists)
    if (item.detections && item.detections.length > 0) {
      doc.text("Detailed Detections", 14, (doc as any).lastAutoTable.finalY + 15);
      
      autoTable(doc, {
        startY: (doc as any).lastAutoTable.finalY + 20,
        head: [["Ticker", "Date", "Score", "Reason"]],
        body: item.detections.map((d: any) => [
          d.ticker,
          d.date,
          d.anomaly_score.toFixed(4),
          d.reason
        ]),
      });
    }

    // 5. Save the file
    doc.save(`Fraud_Report_${item.task_id}.pdf`);
  }
};
