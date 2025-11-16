"""
sample_input.py — Demonstration of Framingham 10-year CVD risk prediction

Loads parameters from data/framingham_params.json and computes risk
for three example cases: Healthy, Average, and Unhealthy.

Source: D’Agostino RB Sr et al., Circulation 2008;117:743–753.
"""

import json
import math
from pathlib import Path
import pandas as pd


# ----------------------------------------------------------------------
# Core computation
# ----------------------------------------------------------------------
def compute_framingham_risk(user):
    PARAM_PATH = Path(__file__).resolve().parent / "framingham_params.json"

    with open(PARAM_PATH, "r") as f:
        FRAMINGHAM_PARAMS = json.load(f)

        
    """Compute 10-year CVD risk using Framingham equations (2008)."""

    sex = user.get("Gender", "Male").lower()
    sbp = user["Systolic_BP"]
    treated = user.get("BP_Treated", False)
    smoker = 1 if user.get("Cigarettes", 0) > 0 else 0
    diabetes = 1 if (
        user.get("Fasting_Glucose_mg_dl", 0) >= 126
        or user.get("HbA1c_percent", 0) >= 6.5
    ) else 0

    # Derive lipid or BMI model choice
    use_lipid = all(
        k in user for k in ["HDL_mg_dl", "LDL_mg_dl", "Triglycerides_mg_dl"]
    )

    # Derive variables
    age = user["Age"]
    if use_lipid:
        hdl = user["HDL_mg_dl"]
        ldl = user["LDL_mg_dl"]
        tg = user["Triglycerides_mg_dl"]
        total_chol = ldl + hdl + tg / 5.0  # Friedewald estimate
    else:
        height_m = user["Height_cm"] / 100
        bmi = user["Weight_kg"] / (height_m**2)

    model_type = "lipid" if use_lipid else "bmi"
    params = FRAMINGHAM_PARAMS[sex][model_type]
    coeff = params["coefficients"]
    s0 = params["baseline_survival"]
    mean_xb = params["mean_xbeta"]

    # Compute log-transformed predictor sum
    xb = 0.0
    xb += coeff["age"] * math.log(age)

    if use_lipid:
        xb += coeff["total_chol"] * math.log(total_chol)
        xb += coeff["hdl_chol"] * math.log(hdl)
    else:
        xb += coeff["bmi"] * math.log(bmi)

    sbp_term = coeff["sbp_treated"] if treated else coeff["sbp_untreated"]
    xb += sbp_term * math.log(sbp)
    xb += coeff["smoker"] * smoker
    xb += coeff["diabetes"] * diabetes

    # Compute final risk
    risk = 1 - (s0 ** math.exp(xb - mean_xb))

    return {
        "sex": sex,
        "model": model_type,
        "xb": xb,
        "mean_xb": mean_xb,
        "risk": risk,
        "baseline_survival": s0,
    }


# ----------------------------------------------------------------------
# Example inputs
# ----------------------------------------------------------------------
test_cases = [
    {
        "Name": "Healthy Female",
        "Gender": "Female",
        "Age": 32,
        "Systolic_BP": 112,
        "BP_Treated": False,
        "HDL_mg_dl": 58,
        "LDL_mg_dl": 110,
        "Triglycerides_mg_dl": 95,
        "Fasting_Glucose_mg_dl": 88,
        "HbA1c_percent": 5.1,
        "Cigarettes": 0,
        "Height_cm": 165,
        "Weight_kg": 62,
    },
    {
        "Name": "Average Male",
        "Gender": "Male",
        "Age": 45,
        "Systolic_BP": 130,
        "BP_Treated": False,
        "HDL_mg_dl": 46,
        "LDL_mg_dl": 145,
        "Triglycerides_mg_dl": 150,
        "Fasting_Glucose_mg_dl": 100,
        "HbA1c_percent": 5.5,
        "Cigarettes": 0,
        "Height_cm": 175,
        "Weight_kg": 80,
    },
    {
        "Name": "Unhealthy Male",
        "Gender": "Male",
        "Age": 55,
        "Systolic_BP": 160,
        "BP_Treated": True,
        "HDL_mg_dl": 35,
        "LDL_mg_dl": 180,
        "Triglycerides_mg_dl": 250,
        "Fasting_Glucose_mg_dl": 160,
        "HbA1c_percent": 7.0,
        "Cigarettes": 15,
        "Height_cm": 170,
        "Weight_kg": 95,
    },
]


# ----------------------------------------------------------------------
# Run demonstration
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("\n🩺 Framingham 10-Year CVD Risk Prediction\n" + "-" * 60)
    results = []
    for user in test_cases:
        res = compute_framingham_risk(user)
        print(
            f"{user['Name']} ({user['Gender']}, {user['Age']}y) — Model: {res['model'].capitalize()}"
        )
        print(f"  Linear Predictor: {res['xb']:.3f}")
        print(f"  10-Year CVD Risk: {res['risk'] * 100:.1f} %\n")
        results.append({**user, **res})

    # Optional: view as DataFrame
    df = pd.DataFrame(results)[
        ["Name", "Gender", "Age", "model", "risk", "xb"]
    ]
    df["risk_percent"] = (df["risk"] * 100).round(1)
    print("-" * 60)
    print(df[["Name", "Gender", "Age", "model", "risk_percent"]])
