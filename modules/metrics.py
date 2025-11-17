import statistics
from modules.scoring import calculate_lifestyle_score
import json
import math
from pathlib import Path

"""Loads parameters from data/framingham_params.json and computes risk
for three example cases: Healthy, Average, and Unhealthy.

Source: D’Agostino RB Sr et al., Circulation 2008;117:743–753.
"""


# ----------------------------------------------------------------------
# Core computation
# ----------------------------------------------------------------------
def compute_framingham_risk(user):
    # Path to the current file (modules/metrics.py)
    current_dir = Path(__file__).parent

    # Go to parent -> then into data/
    PARAM_PATH = current_dir.parent / "data" / "framingham_params.json"

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

    return risk * 100


def calculate_metrics(data):
    metrics = {}

    # 1. BMI and category
    metrics['BMI'] = data['Weight_kg'] / (data['Height_cm'] / 100) ** 2
    if metrics['BMI'] < 18.5:
        metrics['BMI_category'] = "Underweight"
    elif metrics['BMI'] < 25:
        metrics['BMI_category'] = "Normal"
    elif metrics['BMI'] < 30:
        metrics['BMI_category'] = "Overweight"
    elif metrics['BMI'] < 35:
        metrics['BMI_category'] = "Obese Class I"
    elif metrics['BMI'] < 40:
        metrics['BMI_category'] = "Obese Class II"
    else:
        metrics['BMI_category'] = "Obese Class III"

    # 2. Waist-to-height ratio (WHtR) and risk
    metrics['WHtR'] = data['Waist_cm'] / data['Height_cm']
    if metrics['WHtR'] < 0.50:
        metrics['WHtR_risk'] = "Low"
    elif metrics['WHtR'] < 0.60:
        metrics['WHtR_risk'] = "Increased"
    else:
        metrics['WHtR_risk'] = "Very High"
    metrics['WHtR_risk_value'] = round(metrics['WHtR'], 2)

    # 3. Blood pressure (BP) category & risk score
    sbp = data['Systolic_BP']
    dbp = data['Diastolic_BP']
    if sbp < 120 and dbp < 80:
        metrics['BP_category'] = "Normal"
    elif 120 <= sbp < 130 and dbp < 80:
        metrics['BP_category'] = "Elevated"
    elif 130 <= sbp < 140 or 80 <= dbp < 90:
        metrics['BP_category'] = "Hypertension Stage 1"
    else:
        metrics['BP_category'] = "Hypertension Stage 2 or higher"
    metrics['BP_risk_score'] = round(max(0, (sbp - 120) / 20 + (dbp - 80) / 10), 2)

    # 4. Resting Heart Rate risk
    rhr = data['Resting_Heart_Rate']
    metrics['Resting_Heart_Rate'] = rhr
    if rhr <= 60:
        metrics['Heart_Rate_Risk'] = "Optimal"
    elif rhr <= 80:
        metrics['Heart_Rate_Risk'] = "Moderate"
    else:
        metrics['Heart_Rate_Risk'] = "High"
    rr_increment = max(0, rhr - 70) / 10
    metrics['Estimated_RR_increment_%'] = round(rr_increment * 17, 1)

    # 5. Sleep metrics
    sleep_hrs = data.get('Sleep_hours')
    metrics['Sleep_hours_avg'] = sleep_hrs
    if 7 <= sleep_hrs <= 9:
        metrics['Sleep_quality'] = "Adequate"
    elif sleep_hrs < 6:
        metrics['Sleep_quality'] = "Insufficient"
    else:
        metrics['Sleep_quality'] = "Excessive"

    daily = data.get('Daily_records')
    if daily:
        sleep_list = [day['Sleep_hours'] for day in daily]
        metrics['Sleep_std_dev'] = round(statistics.pstdev(sleep_list), 2)
    else:
        metrics['Sleep_std_dev'] = None

    # 6. Sedentary behaviour
    screen_avg = data.get('Screen_hours')
    metrics['Screen_hours_avg'] = screen_avg
    metrics['Sedentary_risk_flag'] = screen_avg > 10

    # 7. Diet quality
    fv_avg = data.get('Fruits') + data.get('Vegetables')
    metrics['Diet_FV_servings_avg'] = round(fv_avg, 1)
    
    if fv_avg >= 10:
        metrics['Diet_quality'] = "Excellent"
    elif fv_avg >= 7:
        metrics['Diet_quality'] = "Good"
    elif fv_avg >= 4:
        metrics['Diet_quality'] = "Moderate"
    else:
        metrics['Diet_quality'] = "Poor"

    # 8. Hydration
    water_avg = data.get('Water_glasses')
    metrics['Water_glasses_avg'] = water_avg
    metrics['Hydration_flag'] = water_avg < 8

    # 9. Lifestyle score & CVD risk
    metrics['Lifestyle_score'] = calculate_lifestyle_score(data)
    metrics['CVD_risk'] = compute_framingham_risk(data)

    # 10. Additional flags
    metrics['Sunlight_min_avg'] = data.get('Sunlight_exposure_min_per_day')
    metrics['Caffeine_cups_per_day'] = data.get('Caffeine_cups_per_day')

    return metrics

