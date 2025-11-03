import statistics
from modules.scoring import calculate_lifestyle_score
from modules.cvd_model import predict_cvd_risk

# =========================================
# MODULE 2: Metric Calculations (Enhanced)
# =========================================

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
    metrics['CVD_risk'] = predict_cvd_risk(data, 'models/cvd_model.pkl')
    
    # 10. Additional flags
    metrics['Sunlight_min_avg'] = data.get('Sunlight_exposure_min_per_day')
    metrics['Caffeine_cups_per_day'] = data.get('Caffeine_cups_per_day')

    return metrics

