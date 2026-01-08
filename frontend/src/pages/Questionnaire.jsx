import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Questionnaire() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    age: "",
    income: "",
    account_balance: "",
    investments: "",
    loan_amount: "",
    interest_rate: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: Number(e.target.value),
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const response = await fetch("http://127.0.0.1:8000/predict-risk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    const data = await response.json();
    navigate("/risk-result", { state: data });
  };

  return (
    <div className="container">
      <div className="card">
        <h1>XAI Stock Risk Analyzer</h1>
        <p className="helper-text">
          Enter approximate values. Exact numbers are not required.
        </p>

        <form onSubmit={handleSubmit}>
          {/* AGE */}
          <label>Age</label>
          <input
            type="number"
            name="age"
            placeholder="e.g. 30"
            onChange={handleChange}
            required
          />
          <div className="helper-text">
            Your current age in years
          </div>

          {/* INCOME */}
          <label>Annual Income (LKR)</label>
          <input
            type="number"
            name="income"
            placeholder="e.g. 75000"
            onChange={handleChange}
            required
          />
          <div className="helper-text">
            Your average yearly income
          </div>

          {/* ACCOUNT BALANCE */}
          <label>Account Balance (LKR)</label>
          <input
            type="number"
            name="account_balance"
            placeholder="e.g. 1200000"
            onChange={handleChange}
            required
          />
          <div className="helper-text">
            Total money available across savings and bank accounts
          </div>

          {/* INVESTMENTS */}
          <label>Total Investments (LKR)</label>
          <input
            type="number"
            name="investments"
            placeholder="e.g. 300000"
            onChange={handleChange}
            required
          />
          <div className="helper-text">
            Value of existing investments (stocks, funds, etc.)
          </div>

          {/* LOAN */}
          <label>Outstanding Loan Amount (LKR)</label>
          <input
            type="number"
            name="loan_amount"
            placeholder="e.g. 200000"
            onChange={handleChange}
            required
          />
          <div className="helper-text">
            Total remaining loans or liabilities
          </div>

          {/* INTEREST RATE */}
          <label>Loan Interest Rate (%)</label>
          <input
            type="number"
            step="0.1"
            name="interest_rate"
            placeholder="e.g. 7.5"
            onChange={handleChange}
            required
          />
          <div className="helper-text">
            Average interest rate of your loans
          </div>

          <br />
          <button type="submit">Analyze Risk</button>
        </form>
      </div>
    </div>
  );
}

export default Questionnaire;
