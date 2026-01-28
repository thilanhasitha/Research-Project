import React, { useState, useEffect } from "react";
import Card from "../../../shared/components/Card";
import Button from "../../../shared/components/Button";
import { fraudService } from "../../../services/fraudService";
import { transformLineData, transformPieData } from "./chartHelpers";
import LineChartComponent from "./LineChartComponent";
import PieChartComponent from "./PieChartComponent";
import {
  MdAnalytics,
  MdScience,
  MdHistory,
  MdFileUpload,
  MdCode,
  MdCloudDownload,
  MdGavel,
  MdScatterPlot,
  MdRadar,
  MdTimeline,
} from "react-icons/md";

const FraudDashboard = () => {
  const [activeModel, setActiveModel] = useState<"m1" | "m2">("m1");
  const [viewMode, setViewMode] = useState<"upload" | "history">("upload");
  const [dataM1, setDataM1] = useState<any>(null);
  const [dataM2, setDataM2] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = "http://localhost:8003";

  useEffect(() => {
    const savedM1 = localStorage.getItem("last_analysis_m1");
    const savedM2 = localStorage.getItem("last_analysis_m2");
    if (savedM1) setDataM1(JSON.parse(savedM1));
    if (savedM2) setDataM2(JSON.parse(savedM2));
  }, []);

  useEffect(() => {
    if (viewMode === "history") {
      setLoading(true);
      fraudService.getHistory().then((data) => {
        const type = activeModel === "m1" ? "Pump & Dump" : "Forensic LSTM";
        setHistory(data.filter((item) => item.model_type === type));
        setLoading(false);
      });
    }
  }, [viewMode, activeModel]);

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setLoading(true);
    try {
      const result = await (activeModel === "m1"
        ? fraudService.uploadPumpDump(file)
        : fraudService.uploadForensicLSTM(file));
      const cleanData = result.data || result;
      if (activeModel === "m1") {
        setDataM1(cleanData);
        localStorage.setItem("last_analysis_m1", JSON.stringify(cleanData));
      } else {
        setDataM2(cleanData);
        localStorage.setItem("last_analysis_m2", JSON.stringify(cleanData));
      }
    } catch (error) {
      alert("Analysis Failed. Ensure backend is running on port 8003.");
    } finally {
      setLoading(false);
    }
  };

  const downloadJSON = (item: any) => {
    const blob = new Blob([JSON.stringify(item, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Forensic_Report_${item.task_id || "Export"}.json`;
    link.click();
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar Navigation */}
      <div className="w-64 bg-slate-900 text-white p-6 space-y-8 flex-shrink-0">
        <div className="flex items-center gap-2 border-b border-slate-700 pb-4">
          <MdGavel className="text-2xl text-blue-400" />
          <h1 className="text-xl font-bold">Forensic AI</h1>
        </div>

        <nav className="space-y-2">
          <p className="text-xs uppercase text-slate-500 font-bold px-4 mb-2">
            Models
          </p>
          <button
            onClick={() => {
              setActiveModel("m1");
              setViewMode("upload");
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${activeModel === "m1" ? "bg-blue-600 shadow-lg" : "hover:bg-slate-800 text-slate-400"}`}
          >
            <MdAnalytics /> Pump & Dump
          </button>
          <button
            onClick={() => {
              setActiveModel("m2");
              setViewMode("upload");
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${activeModel === "m2" ? "bg-purple-600 shadow-lg" : "hover:bg-slate-800 text-slate-400"}`}
          >
            <MdScience /> Forensic LSTM
          </button>
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 p-8 overflow-y-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-800">
              {activeModel === "m1"
                ? "Isolation Forest Engine"
                : "Neural Reconstruction LSTM"}
            </h2>
            <p className="text-slate-500 mt-1">
              {activeModel === "m1"
                ? "Market Manipulation Detection (M1)"
                : "Time-Series Anomaly Analysis (M2)"}
            </p>
          </div>
          <div className="flex bg-slate-200 p-1 rounded-xl">
            <button
              onClick={() => setViewMode("upload")}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${viewMode === "upload" ? "bg-white shadow text-slate-900" : "text-slate-600 hover:text-slate-900"}`}
            >
              Live Analysis
            </button>
            <button
              onClick={() => setViewMode("history")}
              className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${viewMode === "history" ? "bg-white shadow text-slate-900" : "text-slate-600 hover:text-slate-900"}`}
            >
              History Log
            </button>
          </div>
        </div>

        {viewMode === "upload" ? (
          <div className="space-y-8 animate-in fade-in duration-500">
            <Card
              title={`Scan New ${activeModel === "m1" ? "Market" : "Forensic"} Dataset`}
            >
              <div className="flex flex-col items-center p-12 border-2 border-dashed border-slate-300 rounded-2xl bg-white hover:border-blue-400 transition-colors">
                <div
                  className={`p-4 rounded-full mb-4 ${activeModel === "m1" ? "bg-blue-50 text-blue-500" : "bg-purple-50 text-purple-500"}`}
                >
                  <MdFileUpload className="text-4xl" />
                </div>
                <h3 className="text-lg font-semibold text-slate-700">
                  Drop your CSV here
                </h3>
                <p className="text-slate-400 mb-6 text-center max-w-xs">
                  Ensure columns match model requirements before uploading.
                </p>
                <input
                  type="file"
                  id="upload-input"
                  hidden
                  onChange={handleFileUpload}
                />
                <Button
                  onClick={() =>
                    document.getElementById("upload-input")?.click()
                  }
                  disabled={loading}
                  className="px-8"
                >
                  {loading ? "AI Processing..." : "Choose File"}
                </Button>
              </div>
            </Card>

            {activeModel === "m1" && dataM1 && (
              <div className="space-y-8">
                {/* Existing Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card title="Total Rows">
                    <p className="text-3xl font-extrabold">
                      {dataM1.scan_summary.total_rows_processed.toLocaleString()}
                    </p>
                  </Card>
                  <Card title="Scanned Assets">
                    <p className="text-3xl font-extrabold text-blue-600">
                      {dataM1.scan_summary.total_companies_scanned}
                    </p>
                  </Card>
                  <Card title="Detected Frauds">
                    <p className="text-3xl font-extrabold text-red-600">
                      {dataM1.scan_summary.frauds_detected}
                    </p>
                  </Card>
                  <Card title="Flagged Entities">
                    <p className="text-3xl font-extrabold text-orange-500">
                      {dataM1.scan_summary.unique_companies_flagged}
                    </p>
                  </Card>
                </div>

                {/* Existing Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card title="Confidence Timeline (IForest Scoring)">
                    <LineChartComponent
                      chartData={transformLineData(dataM1.detections)}
                    />
                  </Card>
                  <Card title="Risk Distribution">
                    <PieChartComponent chartData={transformPieData(dataM1)} />
                  </Card>
                </div>

                {/* NEW FEATURE 1: CLUSTER MAP & RADAR PROFILE */}
                {/* --- RESEARCH ENHANCEMENT: DYNAMIC VISUALS --- */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Dynamic Anomaly Cluster Map */}
                  <Card
                    title="Anomaly Cluster Projection"
                    className="lg:col-span-2"
                  >
                    <div className="h-64 flex flex-col items-center justify-center bg-slate-100 rounded-xl border border-dashed border-slate-300 relative overflow-hidden">
                      <MdScatterPlot className="text-6xl text-slate-200 absolute opacity-20" />

                      <div className="z-10 text-center">
                        <p className="text-sm font-bold text-slate-600">
                          Spatial Feature Isolation
                        </p>
                        <p className="text-xs text-slate-500 mt-2 bg-white px-3 py-1 rounded-full shadow-sm inline-block border border-slate-200">
                          {/* DYNAMIC TEXT HERE */}
                          Visualizing{" "}
                          <span className="text-red-600 font-bold">
                            {dataM1.detections.length}
                          </span>{" "}
                          outliers vs{" "}
                          <span className="text-slate-900 font-bold">
                            {dataM1.scan_summary.total_rows_processed.toLocaleString()}
                          </span>{" "}
                          baseline coordinates
                        </p>
                        <p className="text-[10px] text-slate-400 mt-3 italic italic">
                          *Isolation Forest mapped across Price/Volume
                          dimensions
                        </p>
                      </div>
                    </div>
                  </Card>

                  {/* Dynamic Risk Dimension Radar */}
                  <Card title="Risk Dimension Radar">
                    <div className="h-64 flex flex-col items-center justify-center bg-slate-100 rounded-xl border border-dashed border-slate-300">
                      <MdRadar className="text-5xl text-blue-300 mb-2 animate-pulse" />
                      <div className="text-center">
                        <p className="text-xs font-bold text-slate-500 uppercase">
                          Feature Contribution
                        </p>
                        <p className="text-[10px] text-slate-400 mb-2">
                          Vol / Price / Frequency
                        </p>

                        {/* DYNAMIC ATTRIBUTE HERE */}
                        <div className="mt-2 bg-slate-200 text-slate-700 text-[10px] px-2 py-1 rounded font-mono">
                          Target: {dataM1.detections[0]?.ticker || "Global Set"}
                        </div>
                        <p className="text-[9px] text-slate-400 mt-1 italic">
                          Weighting based on{" "}
                          {dataM1.scan_summary.unique_companies_flagged} flagged
                          entities
                        </p>
                      </div>
                    </div>
                  </Card>
                </div>

                {/* Existing XAI Table */}
                <Card title="Explainable AI (XAI): Forensic Risk Drivers">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="bg-slate-50 text-slate-500 text-xs font-bold uppercase tracking-wider">
                        <tr>
                          <th className="p-4 border-b">Ticker</th>
                          <th className="p-4 border-b">Risk Factor</th>
                          <th className="p-4 border-b">Impact Score</th>
                          <th className="p-4 border-b">Certainty</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {dataM1.detections.map((d: any, i: number) => (
                          <tr
                            key={i}
                            className="hover:bg-slate-50 transition-colors"
                          >
                            <td className="p-4 font-bold text-slate-700">
                              {d.ticker}
                            </td>
                            <td className="p-4">
                              <span
                                className={`px-3 py-1 rounded-full text-[10px] font-black uppercase ${d.reason.toLowerCase().includes("volume") ? "bg-orange-100 text-orange-700" : "bg-red-100 text-red-700"}`}
                              >
                                {d.reason.toLowerCase().includes("volume")
                                  ? "Volume Surge"
                                  : "Price manipulation"}
                              </span>
                            </td>
                            <td className="p-4 w-64">
                              <div className="flex items-center gap-3">
                                <div className="flex-1 bg-slate-200 rounded-full h-2">
                                  <div
                                    className={`h-full rounded-full ${d.anomaly_score > 0.7 ? "bg-red-500" : "bg-orange-500"}`}
                                    style={{
                                      width: `${d.anomaly_score * 100}%`,
                                    }}
                                  ></div>
                                </div>
                                <span className="text-xs font-mono">
                                  {d.anomaly_score.toFixed(3)}
                                </span>
                              </div>
                            </td>
                            <td className="p-4 text-green-600 font-bold">
                              {Math.floor(d.anomaly_score * 100)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </Card>

                {dataM1.report_url && (
                  <Card title="Spatial Distribution Map">
                    <img
                      src={`${BACKEND_URL}${dataM1.report_url}`}
                      className="w-full rounded-xl"
                      alt="Heatmap"
                    />
                  </Card>
                )}
              </div>
            )}

            {activeModel === "m2" && dataM2 && (
              <div className="space-y-6">
                <Card title="Neural Reconstruction Error Graph (LSTM Evidence)">
                  <img
                    src={`${BACKEND_URL}${dataM2.visual_evidence_url}`}
                    className="w-full rounded-xl shadow-lg"
                    alt="LSTM Plot"
                  />
                </Card>
              </div>
            )}
          </div>
        ) : (
          /* History remains the same */
          <Card
            title={`${activeModel === "m1" ? "Pump & Dump" : "LSTM"} Historical Records`}
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-50 text-slate-600 text-sm font-bold uppercase">
                  <tr>
                    <th className="p-4 border-b">Analysis Timestamp</th>
                    <th className="p-4 border-b">Detected Anomalies</th>
                    <th className="p-4 border-b text-center">Export Data</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.length > 0 ? (
                    history.map((item) => (
                      <tr key={item.task_id} className="hover:bg-slate-50">
                        <td className="p-4 text-slate-700">{item.timestamp}</td>
                        <td className="p-4 font-black text-red-600">
                          {item.scan_summary?.frauds_detected ||
                            item.anomaly_count}
                        </td>
                        <td className="p-4 flex justify-center gap-3">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadJSON(item)}
                            className="gap-2"
                          >
                            <MdCode /> JSON
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => fraudService.downloadPDF(item)}
                            className="gap-2 bg-slate-800"
                          >
                            <MdCloudDownload /> PDF Report
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td
                        colSpan={3}
                        className="p-12 text-center text-slate-400 font-medium italic"
                      >
                        No previous logs found for this model.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default FraudDashboard;
