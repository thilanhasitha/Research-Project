import React from "react";
import styled from "styled-components";
import { MdFileDownload, MdDelete } from "react-icons/md";

// --- Hardcoded History Data ---
const uploadedFilesHistory = [
  {
    id: "FG-001",
    name: "transactions_Q3_2025.csv",
    date: "2025-11-10",
    status: "Completed",
    anomalies: 1204,
    impact: "$1.5M",
  },
  {
    id: "FG-002",
    name: "transactions_oct_2025.csv",
    date: "2025-11-03",
    status: "Completed",
    anomalies: 850,
    impact: "$0.9M",
  },
  {
    id: "FG-003",
    name: "transactions_sep_2025.csv",
    date: "2025-10-27",
    status: "Failed",
    anomalies: 0,
    impact: "$0",
  },
  {
    id: "FG-004",
    name: "transactions_Q2_2025.csv",
    date: "2025-10-15",
    status: "Completed",
    anomalies: 2100,
    impact: "$2.8M",
  },
];

// --- Styled Components ---

const HistoryContainer = styled.div`
  padding: 20px 0;
`;

const SectionTitle = styled.h2`
  color: #c9d1d9;
  margin-bottom: 25px;
  font-size: 24px;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background-color: #161b22;
  border-radius: 8px;
  overflow: hidden;
`;

const Th = styled.th`
  background-color: #1f6feb33; /* Light blue background for header */
  color: #58a6ff;
  text-align: left;
  padding: 15px;
  font-size: 14px;
  border-bottom: 1px solid #30363d;
`;

const Td = styled.td`
  padding: 15px;
  border-bottom: 1px solid #30363d;
  font-size: 14px;
  color: #c9d1d9;
`;

const TbodyRow = styled.tr`
  &:hover {
    background-color: #1e242c;
  }
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: ${(props) => (props.danger ? "#f85149" : "#58a6ff")};
  cursor: pointer;
  margin-right: 10px;
  padding: 5px;

  &:hover {
    opacity: 0.7;
  }
`;

const StatusPill = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: ${(props) => props.color};
  background-color: ${(props) => props.bgColor};
`;

const getStatusStyles = (status) => {
  switch (status) {
    case "Completed":
      return { color: "#2ea043", bgColor: "rgba(46, 160, 67, 0.2)" };
    case "Failed":
      return { color: "#f85149", bgColor: "rgba(248, 81, 73, 0.2)" };
    default:
      return { color: "#8b949e", bgColor: "rgba(139, 148, 158, 0.2)" };
  }
};

// --- Component ---
export default function HistoryContent() {
  return (
    <HistoryContainer>
      <SectionTitle>Uploaded File History</SectionTitle>

      <Table>
        <thead>
          <tr>
            <Th>ID</Th>
            <Th>File Name</Th>
            <Th>Upload Date</Th>
            <Th>Status</Th>
            <Th>Anomalies</Th>
            <Th>Impact</Th>
            <Th>Actions</Th>
          </tr>
        </thead>
        <tbody>
          {uploadedFilesHistory.map((file) => {
            const statusStyles = getStatusStyles(file.status);
            return (
              <TbodyRow key={file.id}>
                <Td>{file.id}</Td>
                <Td>{file.name}</Td>
                <Td>{file.date}</Td>
                <Td>
                  <StatusPill
                    color={statusStyles.color}
                    bgColor={statusStyles.bgColor}
                  >
                    {file.status}
                  </StatusPill>
                </Td>
                <Td>{file.anomalies.toLocaleString()}</Td>
                <Td>{file.impact}</Td>
                <Td>
                  <ActionButton title="Download Report">
                    <MdFileDownload size={18} />
                  </ActionButton>
                  <ActionButton danger title="Delete File">
                    <MdDelete size={18} />
                  </ActionButton>
                </Td>
              </TbodyRow>
            );
          })}
        </tbody>
      </Table>

      <p style={{ marginTop: "20px", color: "#8b949e", fontSize: "14px" }}>
        *Note: This data is hardcoded and simulates a successful history log.
      </p>
    </HistoryContainer>
  );
}
