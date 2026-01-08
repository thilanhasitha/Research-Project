import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const predictRisk = async (userData) => {
  const response = await API.post("/predict-risk", userData);
  return response.data;
};

export const explainRisk = async (userData) => {
  const response = await API.post("/explain-risk", userData);
  return response.data;
};
