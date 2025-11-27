import React from "react";
import styled from "styled-components";
import { MdFileUpload } from "react-icons/md";

// --- Styled Components ---
const Card = styled.div`
  background-color: #161b22;
  border: 2px dashed #30363d;
  border-radius: 8px;
  padding: 50px;
  text-align: center;
  margin-bottom: 40px;
`;

const FileUploadIcon = styled(MdFileUpload)`
  font-size: 48px;
  color: #58a6ff;
  margin-bottom: 15px;
`;

const BrowseButton = styled.button`
  background-color: #238636;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 15px;

  &:hover {
    background-color: #2ea043;
  }
`;

const SmallText = styled.p`
  font-size: 12px;
  color: #8b949e;
  margin-top: 10px;
`;

// --- Component ---
export default function UploadCard() {
  return (
    <Card>
      <FileUploadIcon />
      <p>Upload your transaction data</p>
      <p>Drag and drop your CSV file here or click to browse.</p>
      <BrowseButton>Browse File</BrowseButton>
      <SmallText>Only .csv files are supported. Max file size: 10MB.</SmallText>
    </Card>
  );
}
