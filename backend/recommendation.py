import pandas as pd
from stock_ml.feature_engineering import extract_stock_features
from stock_ml.predict_stock_risk import predict_stock_risk


DATA_PATH = "data/2023 Data.csv"

# Load stock master for company names
stock_master = pd.read_csv(DATA_PATH)

company_map = (
    stock_master[["COMPANY ID", " SHORT NAME "]]
    .drop_duplicates()
    .set_index("COMPANY ID")[" SHORT NAME "]
    .to_dict()
)


def recommend_stocks(user_risk, top_n=5):
    # Extract features from CSV
    features_df = extract_stock_features(DATA_PATH)

    # Predict stock risk using trained ML model
    features_with_risk = predict_stock_risk(features_df)

    # Match with user risk
    matched = features_with_risk[
        features_with_risk["predicted_risk"] == user_risk
    ]

    # Sort by stability (lower volatility = safer)
    matched = matched.sort_values("volatility")

    # Prepare response with explanation
    recommendations = []

    for _, row in matched.head(top_n).iterrows():
        recommendations.append({
            "stock": row["stock"],
            "company_name": company_map.get(row["stock"], row["stock"]),
            "predicted_risk": row["predicted_risk"],
            "volatility": round(row["volatility"], 4),
            "mean_return": round(row["mean_return"], 4),
            "reason": (
                f"This stock matches your {user_risk} risk profile "
                f"with volatility {round(row['volatility'], 4)}."
            )
        })
    


    return recommendations
