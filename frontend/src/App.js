import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Questionnaire from "./pages/Questionnaire";
import RiskResult from "./pages/RiskResult";
import Recommendations from "./pages/Recommendations";


function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/questionnaire" element={<Questionnaire />} />
        <Route path="/risk-result" element={<RiskResult />} />
        <Route path="/recommendations" element={<Recommendations />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;