from modules.visualization import plot_health_dashboard

# -----------------------------
# Helper: interpret overall lifestyle score
# -----------------------------
def interpret_overall_score(score):
    if score >= 85:
        return "Excellent ✅ Keep up the great habits!"
    elif score >= 70:
        return "Good 🙂 Some improvement possible."
    elif score >= 50:
        return "Moderate ⚠️ Focus on key habits."
    else:
        return "Poor ❌ Major lifestyle improvements recommended."
    
def generate_report(data, metrics):
    """
    Generate a polished, comprehensive health report with evidence-based recommendations.
    Includes summary tables, color-coded status, and embedded visualizations.
    """

    # -----------------------------
    # 1. Header
    # -----------------------------
    print("\n" + "="*40)
    print("🏥  ADVANCED HEALTH ASSESSMENT REPORT  🏥")
    print("="*40 + "\n")
    print(f"Age: {data['Age']} | Gender: {data['Gender']}\n")

    # -----------------------------
    # 2. Physical & Anthropometric Metrics
    # -----------------------------
    print("📏  Physical Metrics:")
    print(f"- BMI: {metrics['BMI']:.1f} ({metrics['BMI_category']}) {'✅' if metrics['BMI_category']=='Normal' else '⚠️'}")
    print(f"- Waist-to-Height Ratio: {metrics['WHtR']:.2f} ({metrics['WHtR_risk']}) {'✅' if metrics['WHtR_risk']=='Low' else '⚠️'}")
    print(f"- Blood Pressure: {data['Systolic_BP']}/{data['Diastolic_BP']} mmHg ({metrics['BP_category']})")
    print(f"- Resting Heart Rate: {data['Resting_Heart_Rate']} bpm ({metrics['Heart_Rate_Risk']})\n")

    # -----------------------------
    # 3. Lifestyle Metrics
    # -----------------------------
    print("💪  Lifestyle Metrics:")
    print(f"- Sleep: {data['Sleep_hours']} hrs/night ({metrics['Sleep_quality']})")
    print(f"- Physical Activity: {data['Physical_activity_min'] * 7} min/week")
    print(f"- Fruits & Vegetables: {data['Fruits']} + {data['Vegetables']} servings/day")
    print(f"- Water Intake: {data['Water_glasses']} glasses/day")
    print(f"- Smoking: {data['Cigarettes']} cigarettes/day")
    print(f"- Alcohol: {data['Alcohol_drinks'] * 7} units/week")
    print(f"- Stress Level: {data['Stress_level']} / 10")
    print(f"- Social Interactions: {data['Social_interactions'] * 7} / week\n")

    # -----------------------------
    # 4. Overall Scores
    # -----------------------------
    print("⭐  Summary Scores:")
    print(f"- Lifestyle Score: {metrics['Lifestyle_score']} / 100")
    
    if metrics['CVD_risk'] is not None:
        print(f"🫀 Estimated CVD Risk: {metrics['CVD_risk']}%")
    else:
        print("🫀 CVD Risk: (Could not compute — missing data)")
    print(f"- Overall Health Interpretation: {interpret_overall_score(metrics['Lifestyle_score'])}\n")
    if metrics['CVD_risk'] < 10:
        print("- Your estimated CVD risk is low (<10%). Keep maintaining your healthy habits!")
    elif metrics['CVD_risk'] < 20:
        print("- Your CVD risk is moderate (10–20%). Consider optimizing diet and exercise.")
    else:
        print("- Your CVD risk is high (>20%). Medical screening is advised.")

    # -----------------------------
    # 5. Evidence-Based Recommendations
    # -----------------------------
    print("📝  Recommendations:")

    # Weight management
    if metrics['BMI_category'] in ['Overweight','Obese Class I','Obese Class II','Obese Class III']:
        print("- Aim to reduce body weight by 5–10% to lower metabolic and cardiovascular risk.")
    # Central fat
    if metrics['WHtR_risk'] in ["Increased", "Very High"]:
        print("- Reduce central fat via aerobic activity and balanced diet; aim for WHtR < 0.5.")
    # Sleep
    if metrics['Sleep_quality'] != "Adequate":
        print("- Maintain 7–9 hrs sleep per night to support metabolic, cognitive, and cardiovascular health.")
    # Exercise
    if data['Physical_activity_min'] * 7 < 150:
        print("- Increase moderate-to-vigorous exercise to ≥150 min/week for ~30% lower CVD risk.")
    # Smoking
    if data['Cigarettes'] > 0:
        print("- Quitting smoking reduces heart attack risk by up to 50% within 1 year; consider cessation programs.")
    # Alcohol
    if data['Alcohol_drinks'] * 7 > 14:
        print("- Limit alcohol to ≤7 units/week for liver, BP, and cardiovascular health.")
    # Stress
    if data['Stress_level'] > 6:
        print("- Practice mindfulness, meditation, or breathing exercises to reduce chronic stress.")
    # Diet
    if data['Fruits'] < 5 or data['Vegetables'] < 5:
        print("- Increase fruit & vegetable intake to at least 5 servings each/day.")
    # Hydration
    if data['Water_glasses'] < 8:
        print("- Drink at least 8 glasses of water daily to maintain optimal hydration.")

    print("\n" + "="*40)

    # -----------------------------
    # 6. Visualizations (optional)
    # -----------------------------
    print("\nOpening your interactive dashboard...")
    try:
        plot_health_dashboard(data, metrics)
    except Exception as e:
        print(f"Visualization could not be generated: {e}")

