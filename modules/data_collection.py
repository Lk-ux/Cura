import statistics

# =========================================
# MODULE 1: Data Collection (Enhanced)
# =========================================

def get_valid_number(prompt, min_val=None, max_val=None, allow_blank=False):
    """
    Safely request a numeric input within an optional range.
    Returns float or None (if blank allowed).
    """
    while True:
        val = input(prompt).strip()
        if allow_blank and val == "":
            return None
        try:
            val = float(val)
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"⚠️  Please enter a value between {min_val} and {max_val}.")
                continue
            return val
        except ValueError:
            print("⚠️  Please enter a valid number.")


def get_valid_int(prompt, min_val=None, max_val=None, allow_blank=False):
    """Wrapper for integer validation."""
    val = get_valid_number(prompt, min_val, max_val, allow_blank)
    return int(val) if val is not None else None


def ask_daily_routine(days=7):
    """
    Ask for daily lifestyle info for several days and compute averages.
    This increases accuracy over one-time self-estimates.
    """
    print(f"\nLet's record your routine for {days} days to get accurate averages.")
    print("(Press Enter to reuse yesterday's value)\n")

    fields = {
        "Sleep_hours": "Hours of sleep last night (e.g., 7.5): ",
        "Physical_activity_min": "Minutes of moderate/vigorous exercise today: ",
        "Cigarettes": "Cigarettes smoked today: ",
        "Alcohol_drinks": "Alcoholic drinks consumed today: ",
        "Fruits": "Fruit servings eaten today: ",
        "Vegetables": "Vegetable servings eaten today: ",
        "Water_glasses": "Glasses of water today: ",
        "Screen_hours": "Total recreational screen time today (hours): ",
        "Stress_level": "Stress level today (1-10): ",
        "Social_interactions": "Meaningful social interactions today (number of people): "
    }

    daily_records = []
    prev = {}

    for day in range(1, days + 1):
        print(f"\n📅  Day {day}")
        record = {}
        for key, question in fields.items():
            val = input(question)
            if val.strip() == "" and key in prev:
                val = prev[key]
            else:
                prev[key] = val
            try:
                record[key] = float(val)
            except ValueError:
                record[key] = 0.0
        daily_records.append(record)

    # Compute average for each metric
    averages = {k: round(statistics.mean([day[k] for day in daily_records]), 2) for k in fields.keys()}
    return averages, daily_records


def ask_questions(days_to_log=7):
    """
    Collect physical, metabolic, and lifestyle data with robust validation.
    """
    data = {}
    print("\n🌿 Welcome to the Advanced Health Assessment Tool!")
    print("Please answer as accurately as possible. Units are specified for each question.\n")

    # --- Physical & Demographic ---
    data['Age'] = get_valid_int("Age (years): ", 5, 120)
    data['Gender'] = input("Gender (M/F/Other): ").strip().capitalize()
    data['Height_cm'] = get_valid_number("Height (cm): ", 100, 250)
    data['Weight_kg'] = get_valid_number("Weight (kg): ", 30, 300)
    data['Waist_cm'] = get_valid_number("Waist circumference (cm): ", 40, 200)
    data['Systolic_BP'] = get_valid_int("Systolic BP (mmHg): ", 70, 250)
    data['Diastolic_BP'] = get_valid_int("Diastolic BP (mmHg): ", 40, 150)
    data['Resting_Heart_Rate'] = get_valid_int("Resting heart rate (bpm): ", 30, 200)

    # --- Optional Lab Values (user may skip) ---
    print("\n(Optional) If you have recent lab reports, enter these values; otherwise press Enter.")
    data['HDL_mg_dl'] = get_valid_number("HDL cholesterol (mg/dL): ", 10, 120, allow_blank=True)
    data['LDL_mg_dl'] = get_valid_number("LDL cholesterol (mg/dL): ", 20, 300, allow_blank=True)
    data['Triglycerides_mg_dl'] = get_valid_number("Triglycerides (mg/dL): ", 30, 1000, allow_blank=True)
    data['Fasting_Glucose_mg_dl'] = get_valid_number("Fasting glucose (mg/dL): ", 50, 400, allow_blank=True)
    data['HbA1c_percent'] = get_valid_number("HbA1c (%): ", 3, 15, allow_blank=True)

    # --- Lifestyle (Multi-day routine logging) ---
    print("\nNow let's record your daily lifestyle for more accurate averages.")
    avg_routine, full_routine = ask_daily_routine(days_to_log)
    data.update(avg_routine)
    data['Days_logged'] = days_to_log
    data['Daily_records'] = full_routine

    # --- Additional Wellness Questions ---
    print("\nAdditional questions:")
    data['Occupation_type'] = input("Occupation type (Sedentary / Moderate / Active): ").capitalize()
    data['Diet_type'] = input("Diet type (Omnivore / Vegetarian / Vegan / Other): ").capitalize()
    data['Caffeine_cups_per_day'] = get_valid_int("Cups of caffeinated drinks per day: ", 0, 20)
    data['Sunlight_exposure_min_per_day'] = get_valid_int("Minutes of direct sunlight exposure per day: ", 0, 180)
    data['Sleep_consistency'] = get_valid_int("Bedtime consistency (1-10): ", 1, 10)
    data['Perceived_health_score'] = get_valid_int("How would you rate your overall health (1-10)? ", 1, 10)

    print("\n✅ Data entry complete.")
    return data
