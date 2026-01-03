import React, { useState } from "react";
import styled from "styled-components";
import { MdFileUpload } from "react-icons/md";

const Card = styled.div`
  background-color: #161b22;
  border: 2px dashed #30363d;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  margin-bottom: 30px;
`;

export default function UploadCard({ onUploadSuccess }) {
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Server Error");

      const result = await response.json();
      onUploadSuccess(result);
    } catch (err) {
      alert("Upload Failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <MdFileUpload size={40} color="#58a6ff" />
      <h3 style={{ margin: "10px 0" }}>
        {loading ? "AI Analysis in Progress..." : "Detect Fraud Patterns"}
      </h3>
      <p style={{ color: "#8b949e", marginBottom: "20px" }}>
        Upload your trading CSV file to identify anomalies.
      </p>

      <input
        type="file"
        id="csv-file"
        hidden
        accept=".csv"
        onChange={handleFileChange}
      />
      <button
        style={{
          background: "#238636",
          color: "white",
          padding: "10px 25px",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontWeight: "bold",
        }}
        onClick={() => document.getElementById("csv-file").click()}
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Select CSV File"}
      </button>
    </Card>
  );
}
