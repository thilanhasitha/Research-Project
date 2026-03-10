import pandas as pd
import joblib
import os
import shap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "risk_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "risk_encoder.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "features.pkl")

model = None
scaler = None
risk_encoder = None
FEATURES = None


explainer = None

def load_model():
    global model, scaler, risk_encoder, FEATURES, explainer

    if model is not None:
        return

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    risk_encoder = joblib.load(ENCODER_PATH)
    FEATURES = joblib.load(FEATURES_PATH)

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)

    print("ML model loaded successfully")


def predict_risk(user_input: dict):
    load_model()

    df = pd.DataFrame([user_input])[FEATURES]
    df_scaled = scaler.transform(df)

    pred = model.predict(df_scaled)[0]
    return risk_encoder.inverse_transform([pred])[0]


def explain_prediction(user_input: dict):

    load_model()

    df = pd.DataFrame([user_input])[FEATURES]
    df_scaled = scaler.transform(df)

    # predict class
    pred = model.predict(df_scaled)[0]

    # SHAP explanation
    shap_values = explainer(df_scaled)

    explanation = []

    values = shap_values.values[0]   # SHAP values for this sample

    for i, feature in enumerate(FEATURES):

        value = values[i][pred] if values.ndim == 2 else values[i]

        explanation.append({
            "feature": feature,
            "impact": round(abs(float(value)),4),
            "direction": "increase" if value > 0 else "decrease",
            "message": f"{feature} influenced the risk prediction"
        })

    return explanation
