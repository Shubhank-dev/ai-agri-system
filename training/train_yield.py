import pandas as pd
import numpy as np
import os
import joblib
import time

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score

from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor

# =========================
# LOAD DATA
# =========================
print("📂 Loading dataset...")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(BASE_DIR, "data", "crop_data.csv")

df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

print(f"✅ Data Loaded: {df.shape}")

# =========================
# CLEANING
# =========================
df = df.dropna()

# =========================
# 🎯 TARGET (Yield per hectare)
# =========================
y = df['Yield']

# ✅ IMPORTANT: Area ADD (model ko sense milega)
X = df[['State', 'District', 'Crop', 'Season', 'Crop_Year', 'Area']]

# =========================
# PREPROCESSING
# =========================
categorical = ['State', 'District', 'Crop', 'Season']

# ❌ No scaler needed for tree models
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical)
], remainder='passthrough')

# =========================
# MODELS
# =========================
models = {
    "XGBoost": XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    ),
    "RandomForest": RandomForestRegressor(
        n_estimators=150,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
}

# =========================
# SPLIT
# =========================
print("\n✂️ Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# TRAINING LOOP
# =========================
best_model = None
best_score = float("inf")

print("\n🚀 Starting Training...\n")

for i, (name, model) in enumerate(models.items(), start=1):
    print(f"🔄 Training Model {i}/{len(models)}: {name}")

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    start = time.time()
    pipeline.fit(X_train, y_train)
    end = time.time()

    print(f"⏱️ Time Taken: {round(end - start, 2)} sec")

    # Evaluation
    y_pred = pipeline.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"📊 {name} RMSE: {round(rmse, 4)}")
    print(f"📈 {name} R2: {round(r2, 4)}")
    print("-" * 50)

    if rmse < best_score:
        best_score = rmse
        best_model = pipeline

# =========================
# FINAL MODEL
# =========================
print("\n🎯 FINAL MODEL SELECTED")
print(f"✅ Best RMSE: {round(best_score, 4)}")

y_pred = best_model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n📊 FINAL PERFORMANCE")
print("RMSE:", round(rmse, 4))
print("R2 Score:", round(r2, 4))

# =========================
# SAVE MODEL
# =========================
print("\n💾 Saving model...")

model_path = os.path.join(BASE_DIR, "models", "yield_model.pkl")
joblib.dump(best_model, model_path)

print(f"✅ Model saved at: {model_path}")

print("\n🔥 TRAINING COMPLETE 🔥")