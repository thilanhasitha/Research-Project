import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# ================================
# Load dataset
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "investor_risk_dataset.csv")

df = pd.read_csv(DATA_PATH)

print("Columns:", df.columns.tolist())
print("Dataset shape:", df.shape)

# ================================
# Encode categorical columns
# ================================
categorical_cols = [
    "Occupation",
    "Investment Goals",
    "Loan Purpose",
    "Employment Status",
    "Loan Status"
]

label_encoders = {}

for col in categorical_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

# ================================
# Encode target (Risk Level)
# ================================
risk_encoder = LabelEncoder()
df["Risk Level"] = risk_encoder.fit_transform(df["Risk Level"])

# ================================
# Features & Target (NO LEAKAGE)
# ================================
FEATURES = [
    "Age",
    "Income Level",
    "Account Balance",
    "Investments",
    "Loan Amount",
    "Interest Rate"
]

X = df[FEATURES].copy()
y = df["Risk Level"]



# ================================
# Train-test split
# ================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ================================
# Scale features
# ================================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ================================
# Train model
# ================================
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train_scaled, y_train)

# ================================
# Evaluation
# ================================
y_pred = model.predict(X_test_scaled)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ================================
# Save artifacts
# ================================
joblib.dump(model, "risk_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(risk_encoder, "risk_encoder.pkl")
joblib.dump(FEATURES, "features.pkl")


print("\nModel training completed and saved!")
