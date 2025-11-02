def calculate_lifestyle_score(data):
    """
    Compute evidence‐based lifestyle score (0-100) based on a range of behaviours.
    Inputs: data dictionary with averaged daily/week behaviours from Module 1.
    """
    score = 0.0
    max_score = 100.0

    # 1. Physical Activity (max 20 pts)
    if data.get('Physical_activity_min') is not None:
        if data['Physical_activity_min'] >= 150:
            score += 20
        elif data['Physical_activity_min'] >= 90:
            score += 14
        else:
            score += 5

    # 2. Smoking (max 15 pts)
    cig = data.get('Cigarettes')
    if cig is not None:
        if cig == 0:
            score += 15
        elif cig <= 5:
            score += 8
        else:
            score += 2

    # 3. Diet Quality (fruits + vegetables) (max 15 pts)
    fruits = data.get('Fruits', 0.0)
    vegs   = data.get('Vegetables', 0.0)
    # target: fruits ≥ 2 servings/day and vegs ≥ 3 servings/day (example) 
    diet_fraction = min(fruits / 2.0, 1.0) * 0.5 + min(vegs / 3.0, 1.0) * 0.5
    score += diet_fraction * 15

    # 4. Sleep Duration & Regularity (max 12 pts)
    sleep = data.get('Sleep_hours')
    std_dev_sleep = data.get('Sleep_std_dev', None)
    if sleep is not None:
        if 7 <= sleep <= 9:
            base = 10
        elif 6 <= sleep < 7 or 9 < sleep <= 10:
            base = 6
        else:
            base = 3
        if std_dev_sleep is not None and std_dev_sleep < 1.0:
            # if consistent sleep
            base += 2
        score += base

    # 5. Sedentary Behaviour / Screen Time (max 8 pts)
    screen = data.get('Screen_hours')
    if screen is not None:
        if screen <= 4:
            score += 8
        elif screen <= 8:
            score += 5
        else:
            score += 2

    # 6. Alcohol Consumption (max 8 pts)
    alc = data.get('Alcohol_drinks')
    if alc is not None:
        if alc == 0:
            score += 8
        elif alc <= 7:
            score += 5
        else:
            score += 1

    # 7. Hydration (max 5 pts)
    water = data.get('Water_glasses', 0.0)
    hydration_fraction = min(water / 8.0, 1.0)
    score += hydration_fraction * 5

    # 8. Stress Level (max 5 pts) — lower stress = better
    stress = data.get('Stress_level')
    if stress is not None:
        # invert: scale (1 is lowest stress, 10 highest)
        stress_score = max(0, (10 - stress) / 9.0)
        score += stress_score * 5

    # 9. Social Interactions (max 4 pts)
    social = data.get('Social_interactions')
    if social is not None:
        fraction_social = min(social / 5.0, 1.0)
        score += fraction_social * 4

    # 10. Sunlight Exposure / Caffeine / Diet‐Type / Occupation – bonus (max 3 pts)
    sunlight = data.get('Sunlight_min')
    caffeine = data.get('Caffeine_cups_per_day')
    bonus = 0.0
    if sunlight is not None and sunlight >= 30:
        bonus += 1.0
    if caffeine is not None and caffeine <= 3:
        bonus += 1.0
    diet_type = data.get('Diet_type', "").lower()
    if diet_type in ['vegetarian','vegan','omnivore']:
        bonus += 1.0
    score += bonus  # up to 3

    # Ensure not above max_score
    final_score = round(min(score, max_score), 1)
    return final_score

