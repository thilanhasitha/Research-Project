# future work
import joblib
import shap
import pandas as pd

MODEL_PATH = "stock_model.pkl"

def explain_stock(stock_features):
    saved = joblib.load(MODEL_PATH)

    model = saved["model"]
    encoder = saved["encoder"]
    feature_names = saved["features"]

    df = pd.DataFrame([stock_features])[feature_names]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(df)

    explanation = []

    for i, f in enumerate(feature_names):
        value = shap_values[0][0][i]
        explanation.append({
            "feature": f,
            "impact": float(value),
            "direction": "increase" if value > 0 else "decrease"
        })

    return explanation
