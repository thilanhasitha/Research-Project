import { Link } from "react-router-dom";

function Navbar() {
  return (
    <div className="navbar">
      <h2>XAI Stock Analyzer</h2>
      <div>
        <Link to="/">Home</Link>
        <Link to="/questionnaire">Analyze Risk</Link>
      </div>
    </div>
  );
}

export default Navbar;
