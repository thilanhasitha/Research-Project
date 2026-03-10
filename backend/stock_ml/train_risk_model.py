import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils import resample

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

print("\nClass mapping:")
for i, label in enumerate(risk_encoder.classes_):
    print(label, "->", i)

# ================================
# Balance dataset
# ================================
low_class = list(risk_encoder.classes_).index("Low")
medium_class = list(risk_encoder.classes_).index("Medium")
high_class = list(risk_encoder.classes_).index("High")

df_low = df[df["Risk Level"] == low_class]
df_medium = df[df["Risk Level"] == medium_class]
df_high = df[df["Risk Level"] == high_class]

# Upsample high risk
df_high_upsampled = resample(
    df_high,
    replace=True,
    n_samples=1500,
    random_state=42
)

# Combine
df = pd.concat([df_low, df_medium, df_high_upsampled])

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("\nBalanced dataset distribution:")
print(df["Risk Level"].value_counts())

# ================================
# Features & Target
# ================================
FEATURES = [
    "Age",
    "Income Level",
    "Account Balance",
    "Investments",
    "Loan Amount",
    "Interest Rate"
]

X = df[FEATURES]
y = df["Risk Level"]

# ================================
# Train-test split
# ================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
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
    n_estimators=300,
    random_state=42,
    class_weight={low_class: 1, medium_class: 2, high_class: 6}
)

model.fit(X_train_scaled, y_train)

# ================================
# Evaluation
# ================================
y_pred = model.predict(X_test_scaled)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# ================================
# Save artifacts
# ================================
joblib.dump(model, os.path.join(BASE_DIR, "risk_model.pkl"))
joblib.dump(scaler, os.path.join(BASE_DIR, "scaler.pkl"))
joblib.dump(risk_encoder, os.path.join(BASE_DIR, "risk_encoder.pkl"))
joblib.dump(FEATURES, os.path.join(BASE_DIR, "features.pkl"))

print("\nModel training completed and saved!")