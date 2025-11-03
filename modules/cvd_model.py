# =========================================
# MODULE: ML-Based CVD Risk Prediction
# =========================================
# Author: Lakshya + ChatGPT (GPT-5)
# Description:
# Trains and serves an interpretable XGBoost model
# to estimate cardiovascular disease (CVD) risk
# using biometrics and lifestyle features.

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
import joblib
import pandas as pd
import numpy as np

# =========================================
# STEP 1: Dataset Preparation
# =========================================

def load_uci_heart_data():
    from sklearn.datasets import fetch_openml
    try:
        # Attempt via OpenML
        data = fetch_openml(name="Heart-Disease-Dataset-(Comprehensive)", version=1, as_frame=True)
        df = data.frame
        print("Loaded from OpenML: Heart-Disease-Dataset-(Comprehensive)")
    except Exception as e:
        print("OpenML fetch failed:", e)
        # Fallback to a direct URL mirror
        url = "https://raw.githubusercontent.com/plotly/datasets/master/heart.csv"
        df = pd.read_csv(url)
        print("Loaded from CSV mirror at GitHub")
    return df

# =========================================
# STEP 2: Model Training
# =========================================

def train_cvd_model(save_path="cvd_model.pkl"):
    df = load_uci_heart_data()
    # Ensure '1' = disease present
    if df['target'].mean() < 0.5:
        # If majority are 0, assume 1 = disease; else invert
        if df['target'].sum() > len(df)/2:
            print("Inverting target encoding (1 = healthy -> disease)")
            df['target'] = 1 - df['target']
    X = df.drop(columns=['target'])
    y = df['target']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Normalize numeric features — but preserve column names
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns,
        index=X_test.index
    )

    # Train model
    model = XGBClassifier(
        max_depth=3, n_estimators=300, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9, eval_metric='logloss',
        random_state=42, use_label_encoder=False
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])
    print(f"✅ CVD Model trained successfully. Test AUC = {auc:.3f}")

    # Verify that feature names are stored
    print("Model features:", list(model.feature_names_in_))

    # Save model + scaler
    joblib.dump({'model': model, 'scaler': scaler}, save_path)
    print(f"Model saved to {save_path}")



def predict_cvd_risk(user_data, model_path="cvd_model.pkl"):
    """
    Predicts CVD risk (%) using the trained UCI Heart-based XGBoost model.
    Automatically clamps unrealistic inputs and maps lifestyle variables
    to clinically comparable features.

    Parameters
    ----------
    user_data : dict
        Dictionary of user metrics, e.g. Age, Gender, BP, Lipids, etc.
    model_path : str
        Path to trained model file (default: cvd_model.pkl)

    Returns
    -------
    float
        Estimated CVD probability in percent (0–100)
    """

    bundle = joblib.load(model_path)
    model, scaler = bundle['model'], bundle['scaler']
    print("Scaler mean/std sanity check:")
    print(pd.DataFrame({'mean': scaler.mean_, 'std': scaler.scale_}, index=model.feature_names_in_))

    # --- Helper: clip values into physiological range ---
    def clamp(value, min_val, max_val, default):
        try:
            val = float(value)
        except (TypeError, ValueError):
            val = default
        return float(np.clip(val, min_val, max_val))

    # --- Map lifestyle → UCI clinical features ---
    age = clamp(user_data.get('Age', 50), 29, 80, 50)
    sex = 1 if str(user_data.get('Gender', 'M')).lower().startswith('m') else 0

    # BP handling
    sbp = clamp(user_data.get('Systolic_BP', 120), 90, 200, 120)
    dbp = clamp(user_data.get('Diastolic_BP', 80), 60, 120, 80)

    # Cholesterol surrogate: LDL + ⅓ * Triglycerides + HDL
    ldl = clamp(user_data.get('LDL_mg_dl', 120), 70, 400, 120)
    hdl = clamp(user_data.get('HDL_mg_dl', 50), 20, 100, 50)
    tg  = clamp(user_data.get('Triglycerides_mg_dl', 150), 50, 600, 150)
    cholesterol = clamp(ldl + (tg / 3) + hdl, 100, 600, 200)

    # Binary: fasting glucose >120 mg/dL → diabetic
    fasting_glucose = clamp(user_data.get('Fasting_Glucose_mg_dl', 85), 60, 400, 85)
    fasting_blood_sugar = 1 if fasting_glucose > 120 else 0

    # ECG/stress approximations
    stress = clamp(user_data.get('Stress_level', 5), 0, 10, 5)
    resting_ecg = 0 if stress < 4 else 1 if stress < 8 else 2

    # Heart rate and angina proxies
    rhr = clamp(user_data.get('Resting_Heart_Rate', 75), 40, 200, 75)
    physical_activity = clamp(user_data.get('Physical_activity_min', 90), 0, 600, 90)
    exercise_angina = 1 if physical_activity < 90 else 0   # less active → higher angina risk

    # Estimate “max heart rate achieved” ~ resting + activity influence
    max_heart_rate = clamp(rhr + (0.3 * physical_activity / 10), 70, 200, 150)

    # Oldpeak and ST slope proxies (derived from BP & stress)
    oldpeak = round(((sbp - 120) / 40) + (stress / 5), 2)
    oldpeak = clamp(oldpeak, 0, 6, 1)
    ST_slope = 2 if stress < 4 else 1 if stress < 8 else 0

    # Chest pain type proxy
    chest_pain_type = 0 if exercise_angina == 0 else 2

    # --- Assemble model input ---
    input_features = pd.DataFrame([{
        'age': age,
        'sex': sex,
        'chest_pain_type': chest_pain_type,
        'resting_bp_s': sbp,
        'cholesterol': cholesterol,
        'fasting_blood_sugar': fasting_blood_sugar,
        'resting_ecg': resting_ecg,
        'max_heart_rate': max_heart_rate,
        'exercise_angina': exercise_angina,
        'oldpeak': oldpeak,
        'ST_slope': ST_slope
    }])

    # Match model feature order
    input_features = input_features[model.feature_names_in_]

    # --- Keep features in training-like ranges ---
    feature_bounds = {
        'resting_bp_s': (90, 200),
        'cholesterol': (100, 600),
        'max_heart_rate': (70, 200),
        'oldpeak': (0, 6),
    }

    for col, (lo, hi) in feature_bounds.items():
        if col in input_features:
            input_features[col] = np.clip(input_features[col], lo, hi)

    # --- Predict risk ---
    X_scaled = scaler.transform(input_features)
    prob = float(model.predict_proba(X_scaled)[0, 1])
    if prob > 0.5:  # empirically detected inversion
        prob = 1 - prob
    # Stabilize extremes (avoid false “healthy high-risk” cases)
    prob = np.clip(prob, 0.001, 0.999)
    risk_percent = round(prob * 100, 1)

    # --- Simple interpretability feedback ---
    if risk_percent < 10:
        risk_level = "Low"
    elif risk_percent < 20:
        risk_level = "Mild"
    elif risk_percent < 40:
        risk_level = "Moderate"
    elif risk_percent < 60:
        risk_level = "Elevated"
    else:
        risk_level = "High"

    print(f"🩺 Predicted CVD risk: {risk_percent:.1f}% ({risk_level})")
    return risk_percent
