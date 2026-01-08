import pandas as pd
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "stock_ml", "risk_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "stock_ml", "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "stock_ml", "risk_encoder.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "stock_ml", "features.pkl")

model = None
scaler = None
risk_encoder = None
FEATURES = None


def load_model():
    global model, scaler, risk_encoder, FEATURES

    if model is not None:
        return

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    risk_encoder = joblib.load(ENCODER_PATH)
    FEATURES = joblib.load(FEATURES_PATH)

    print(" ML model loaded successfully")
    print(" Features used:", FEATURES)


def predict_risk(user_input: dict):
    load_model()

    df = pd.DataFrame([user_input])[FEATURES]
    df_scaled = scaler.transform(df)

    pred = model.predict(df_scaled)[0]
    return risk_encoder.inverse_transform([pred])[0]


def explain_prediction(user_input: dict):
  
    explanations = []

    if user_input["Age"] < 30:
        explanations.append("Younger age increases financial risk exposure.")
    elif user_input["Age"] < 50:
        explanations.append("Middle-age profile has moderate financial risk.")

    if user_input["Income Level"] < 50000:
        explanations.append("Lower income increases financial risk.")
    else:
        explanations.append("Stable income reduces financial risk.")

    if user_input["Loan Amount"] > 50000:
        explanations.append("High loan amount increases financial risk.")

    if user_input["Interest Rate"] > 10:
        explanations.append("High interest rate increases repayment risk.")

    return explanations
