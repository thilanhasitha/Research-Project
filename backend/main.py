from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import responses_collection
from model import predict_risk, explain_prediction
from recommendation import recommend_stocks
from model import load_model
load_model()


app = FastAPI(title="XAI Stock Recommendation API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    age: int
    income: float
    account_balance: float
    investments: float
    loan_amount: float
    interest_rate: float



@app.post("/predict-risk")
def predict(user_input: UserInput):
    data = user_input.dict()

    # Predict user risk
    ml_input = {
        "Age": data["age"],
        "Income Level": data["income"],
        "Account Balance": data["account_balance"],
        "Investments": data["investments"],
        "Loan Amount": data["loan_amount"],
        "Interest Rate": data["interest_rate"]
    }


    risk = predict_risk(ml_input)
    explanation = explain_prediction(ml_input)


    # Recommend stocks
    recommendations = recommend_stocks(risk)

    # Store in MongoDB
    responses_collection.insert_one({
        **data,
        "risk_level": risk,
        "explanation": explanation,
        "recommendations": recommendations
    })

    return {
        "risk_level": risk,
        "explanation": explanation,
        "recommendations": recommendations
    }


