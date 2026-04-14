import pandas as pd
import numpy as np
import joblib
import os
import time

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error

from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

# =========================
# PATH SETUP
# =========================
print("📂 Loading dataset...")
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(BASE_DIR, "data", "price_data.csv")

df = pd.read_csv(file_path)
df.columns = df.columns.str.strip()

print("✅ Data Loaded:", df.shape)

# =========================
# CLEAN DATA
# =========================
df = df[df['State'] == 'Uttar Pradesh']

df = df.rename(columns={
    'Commodity': 'Crop',
    'Modal Price (Rs./Quintal)': 'Price',
    'Price Date': 'Date',
    'District Name': 'District',
    'Market Name': 'Market'
})

df = df.dropna(subset=['Crop', 'Price', 'Date'])

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

print("✅ Cleaned Data:", df.shape)

# =========================
# FEATURE ENGINEERING
# =========================
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Season'] = df['Month'] % 12 // 3

# =========================
# FEATURES & TARGET
# =========================
X = df[['Crop', 'District', 'Month', 'Season']]
y = df['Price']

# =========================
# PREPROCESSING
# =========================
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['Crop', 'District'])
], remainder='passthrough')

# =========================
# MODELS
# =========================
models = {
    "RandomForest": RandomForestRegressor(
        random_state=42,
        n_jobs=-1
    ),
    "XGBoost": XGBRegressor(
        random_state=42,
        n_jobs=-1
    )
}

# =========================
# PARAM GRIDS
# =========================
param_grids = {
    "RandomForest": {
        'model__n_estimators': [100, 150],
        'model__max_depth': [10, 15]
    },
    "XGBoost": {
        'model__n_estimators': [200],
        'model__max_depth': [5, 7],
        'model__learning_rate': [0.05, 0.1]
    }
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

total_models = len(models)
count = 1

print("\n🚀 Starting Price Model Training...\n")

for name, model in models.items():

    print(f"🔄 Training Model {count}/{total_models}: {name}")

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    print("⚙️ Applying Hyperparameter Tuning...")

    grid = GridSearchCV(
        pipeline,
        param_grids[name],
        cv=3,
        scoring='neg_mean_absolute_error',
        verbose=2,
        n_jobs=-1
    )

    start = time.time()
    grid.fit(X_train, y_train)
    end = time.time()

    print(f"⏱️ Time Taken: {round(end-start,2)} sec")

    y_pred = grid.best_estimator_.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"📊 {name} MAE: {round(mae,2)}")
    print("🏆 Best Params:", grid.best_params_)
    print("-" * 50)

    if mae < best_score:
        best_score = mae
        best_model = grid.best_estimator_

    count += 1

# =========================
# FINAL EVALUATION
# =========================
print("\n🎯 FINAL MODEL SELECTED")
print(f"✅ Best MAE: {round(best_score,2)}")

y_pred = best_model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

print("\n📊 FINAL PERFORMANCE")
print("MAE:", round(mae,2))

# =========================
# SAMPLE TEST
# =========================
sample = pd.DataFrame({
    'Crop': ['Potato'],
    'District': ['Agra'],
    'Month': [3],
    'Season': [3 % 12 // 3]
})

pred_price = best_model.predict(sample)[0]

print("\n💰 Sample Prediction:", round(pred_price, 2))

# =========================
# SAVE MODEL
# =========================
print("\n💾 Saving best model...")

model_path = os.path.join(BASE_DIR, "models", "price_model.pkl")
joblib.dump(best_model, model_path)

print(f"✅ Model saved at: {model_path}")

print("\n🔥 PRICE MODEL TRAINING COMPLETE 🔥")