import statistics
from modules.scoring import calculate_lifestyle_score

# =========================================
# MODULE 2: Metric Calculations (Enhanced)
# =========================================
def estimate_cvd_risk(data):
    """
    Estimate CVD risk using multiple health and lifestyle factors.
    
    Parameters:
    - data: dict containing personal, clinical, and lifestyle information
    
    Returns:
    - risk: float, estimated risk percentage (0–100)
    """
    risk = 0.0
    
    # Age
    age = data.get("Age", 30)
    risk += max(age - 30, 0) * 0.5  # modest increase per year over 30
    
    # Gender
    if data.get("Gender", "Female").lower() == "male":
        risk += 5
    
    # BMI
    height_m = data.get("Height_cm", 170) / 100
    weight_kg = data.get("Weight_kg", 70)
    bmi = weight_kg / (height_m ** 2)
    if bmi >= 30:
        risk += 5
    elif bmi >= 25:
        risk += 2
    
    # Blood pressure
    sbp = data.get("Systolic_BP", 120)
    dbp = data.get("Diastolic_BP", 80)
    if sbp >= 140 or dbp >= 90:
        risk += 5
    elif sbp >= 120 or dbp >= 80:
        risk += 2
    
    # Lipids
    hdl = data.get("HDL_mg_dl", 50)
    ldl = data.get("LDL_mg_dl", 100)
    triglycerides = data.get("Triglycerides_mg_dl", 150)
    if hdl < 40:
        risk += 3
    if ldl >= 160:
        risk += 5
    elif ldl >= 130:
        risk += 2
    if triglycerides >= 200:
        risk += 2
    
    # Blood sugar / diabetes
    glucose = data.get("Fasting_Glucose_mg_dl", 100)
    hba1c = data.get("HbA1c_percent", 5.0)
    if glucose >= 126 or hba1c >= 6.5:
        risk += 5
    elif glucose >= 100 or hba1c >= 5.7:
        risk += 2
    
    # Smoking
    cigarettes = data.get("Cigarettes", 0)
    if cigarettes > 0:
        risk += 5
    
    # Alcohol
    alcohol = data.get("Alcohol_drinks", 0)
    if alcohol >= 7:  # heavy drinking
        risk += 3
    
    # Physical activity
    activity_min = data.get("Physical_activity_min", 0)
    if activity_min < 150:  # less than recommended 150 min/week
        risk += 2
    
    # Sleep
    sleep_hours = data.get("Sleep_hours", 7)
    if sleep_hours < 6 or sleep_hours > 9:
        risk += 1
    
    # Diet quality (fruits & vegetables)
    fruits = data.get("Fruits", 0)
    vegetables = data.get("Vegetables", 0)
    if fruits + vegetables < 5:
        risk += 2
    
    # Stress
    stress = data.get("Stress_level", 5)
    risk += max(0, (stress - 5) * 0.5)  # higher stress slightly increases risk
    
    # Sedentary behavior
    screen_hours = data.get("Screen_hours", 5)
    if screen_hours > 8:
        risk += 1
    
    # Cap risk at 100%
    risk = min(risk, 100)
    
    return risk

# Example usage
risk = estimate_cvd_risk_extended(data)
print(f"Estimated 10-year CVD risk: {risk:.1f}%")


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
    # simple continuous risk score
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
    # estimate relative increase in mortality risk: +17% per +10 bpm above baseline ~70 bpm
    rr_increment = max(0, rhr - 70) / 10
    metrics['Estimated_RR_increment_%'] = round(rr_increment * 17, 1)

    # 5. Sleep metrics
    # We assume data includes average sleep hours and optionally full daily records.
    sleep_hrs = data.get('Sleep_hours')
    metrics['Sleep_hours_avg'] = sleep_hrs
    if 7 <= sleep_hrs <= 9:
        metrics['Sleep_quality'] = "Adequate"
    elif sleep_hrs < 6:
        metrics['Sleep_quality'] = "Insufficient"
    else:
        metrics['Sleep_quality'] = "Excessive"

    # If daily records exist: compute sleep variability
    daily = data.get('Daily_records')
    if daily:
        sleep_list = [day['Sleep_hours'] for day in daily]
        metrics['Sleep_std_dev'] = round(statistics.pstdev(sleep_list), 2)
    else:
        metrics['Sleep_std_dev'] = None

    # 6. Sedentary behaviour (screen time)
    screen_avg = data.get('Screen_hours')
    metrics['Screen_hours_avg'] = screen_avg
    metrics['Sedentary_risk_flag'] = screen_avg > 10  # flag if >10h/day

    # 7. Diet quality derived metric
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

    # 8. Hydration sufficiency
    water_avg = data.get('Water_glasses')
    metrics['Water_glasses_avg'] = water_avg
    metrics['Hydration_flag'] = water_avg < 8

    # 9. Lifestyle composite score & CVD risk reduction
    metrics['Lifestyle_score'] = calculate_lifestyle_score(data)
    # CVD risk prediction (ML-based)
    metrics['CVD_risk'] = estimate_cvd_risk(data)
    
    # 10. Additional flags
    metrics['Sunlight_min_avg'] = data.get('Sunlight_exposure_min_per_day')
    metrics['Caffeine_cups_per_day'] = data.get('Caffeine_cups_per_day')

    return metrics

