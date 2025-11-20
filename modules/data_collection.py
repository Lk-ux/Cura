import statistics

# =========================================
# MODULE 1: Data Collection 
# =========================================
def get_meal_list(meal_name):
    """
    Collect a list of foods for a single meal.
    Example return:
    [
        {"item": "egg", "quantity": 2},
        {"item": "roti", "quantity": 1}
    ]
    """

    print(f"\n🍽️  Enter items for {meal_name} (press Enter with no item to stop)")

    meal_items = []
    prev_item = None
    prev_qty = 1

    while True:
        item = input("Food item: ").strip().lower()

        # Stop meal entry
        if item == "":
            break

        # Reuse previous entry
        if item == "same" and prev_item:
            item = prev_item
            qty = prev_qty
        else:
            # Validate quantity
            qty = input("Quantity: ").strip()
            try:
                qty = int(qty)
                if qty <= 0:
                    print("⚠️ Quantity must be positive.")
                    continue
            except ValueError:
                print("⚠️ Enter a valid whole number.")
                continue

        meal_items.append({"item": item, "quantity": qty})
        prev_item, prev_qty = item, qty

    return meal_items

def ask_daily_meals(days=7):
    """
    Asks the user to enter breakfast, lunch, dinner for each day.
    Allows reusing the previous day's meals.
    Returns:
      - average meals (flattened)
      - full meal logs per day
    """

    print(f"\nLet's record your meals for {days} days (to improve nutrition accuracy).")
    print("Tip: Type 'same' to reuse the last food item. Press Enter on 'Food item' to stop a meal.")

    all_days = []
    prev_day_meals = {}

    for day in range(1, days + 1):
        print(f"\n📅  Day {day} — Meal Logging")

        day_meals = {}

        for meal_name in ["Breakfast", "Lunch", "Dinner"]:
            reuse = input(f"Reuse yesterday's {meal_name.lower()}? (y/N): ").lower().strip()
            if reuse == "y" and meal_name in prev_day_meals:
                day_meals[meal_name] = prev_day_meals[meal_name].copy()
                print(f"✔️ Reused {meal_name.lower()} from yesterday.")
                continue

            day_meals[meal_name] = get_meal_list(meal_name)

        all_days.append(day_meals)
        prev_day_meals = day_meals  # allow reuse tomorrow

    # Flatten meals to daily average data
    # Summarization stays in nutrition module — here we only collect raw logs
    return all_days


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


def ask_daily_routine(days=1):
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


def ask_questions(days_to_log=1):
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

    # --- Daily Nutrition Logging (Multi-day Meals) ---
    print("\nNow let's record your meals for better nutrition insights.")
    meal_logs = ask_daily_meals(days_to_log)
    data['Meal_logs'] = meal_logs

    # --- Additional Wellness Questions ---
    print("\nAdditional questions:")
    data['Occupation_type'] = input("Occupation type (Sedentary / Moderate / Active): ").capitalize()
    data['Diet_type'] = input("Diet type (Omnivore / Vegetarian / Vegan / Other): ").capitalize()
    data['Caffeine_cups_per_day'] = get_valid_int("Cups of caffeinated drinks per day: ", 0, 20)
    data['Sunlight_exposure_min_per_day'] = get_valid_int("Minutes of direct sunlight exposure per day: ", 0, 180)
    data['Sleep_consistency'] = get_valid_int("Bedtime consistency (1-10): ", 1, 10)
    data['Perceived_health_score'] = get_valid_int("How would you rate your overall health (1-10)? ", 1, 10)

    print("\n✅ Data entry complete.")

    # Prepare a single-day average style structure for nutrition module
    # Take the last day's meals as representative (or compute your own logic)
    if meal_logs:
        last_day = meal_logs[-1]
        data['meals'] = [
            last_day.get("Breakfast", []),
            last_day.get("Lunch", []),
            last_day.get("Dinner", [])
        ]

    return data



