"""
nutrition.py
-------------
Offline-only nutrition module.
Goal: **Create less, use more** → reuse robust existing data (CSV) and avoid
inventing data.

Key Principles:
- Offline-only (no APIs).
- Loads a single canonical CSV from data/offline_nutrients.csv.
- No hallucination: unknown foods are skipped, never fabricated.
- Clean + predictable dictionary-based outputs.
- Shared logic from both earlier designs merged into one.
"""

from typing import List, Dict
import os
import csv

# ---------------------------------------------------------------------
# LOAD OFFLINE FOOD DATABASE (single source of truth)
# ---------------------------------------------------------------------

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "offline_nutrients.csv")


def _load_offline_db() -> Dict[str, Dict]:
    """Loads CSV into a dict:
    {
        "roti (1 medium)": {"cal":120,"protein":3,"carbs":22,"fat":2},
        ...
    }
    Keys normalized to lowercase for robust lookup.
    """
    db = {}
    if not os.path.exists(DATA_PATH):
        return db

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["description"].strip().lower()
            db[name] = {
                "cal": float(row.get("calories", 0)),
                "protein": float(row.get("protein_g", 0)),
                "fat": float(row.get("fat_g", 0)),
                "carbs": float(row.get("carbs_g", 0)),
            }
    return db


# Lazy-loaded singleton DB
BASIC_NUTRITION_DB = _load_offline_db()


# ---------------------------------------------------------------------
# 1) MEAL ANALYSIS
# meals = list of dicts: [{"item": "roti (1 medium)", "quantity": 2}, ...]
# ---------------------------------------------------------------------

def analyze_meal(meals: List[Dict]) -> Dict:
    """Returns calorie + macro totals using the offline DB.
    Unknown foods → added to unknown_items list (no made-up data).
    """

    total = {"cal": 0, "protein": 0, "carbs": 0, "fat": 0}
    unknown_items = []

    for entry in meals:
        item = str(entry.get("item", "")).lower()
        qty = entry.get("quantity", 1)

        if item in BASIC_NUTRITION_DB:
            info = BASIC_NUTRITION_DB[item]
            total["cal"] += info["cal"] * qty
            total["protein"] += info["protein"] * qty
            total["carbs"] += info["carbs"] * qty
            total["fat"] += info["fat"] * qty
        else:
            unknown_items.append(item)

    return {
        "totals": total,
        "unknown_items": unknown_items,
        # simple heuristics
        "protein_low": total["protein"] < 50,
        "fiber_low": total["carbs"] < 80,
    }


# ---------------------------------------------------------------------
# 2) DAILY SUMMARY ACROSS ALL MEALS
# all_meals = [breakfast=[...], lunch=[...], dinner=[...]]
# ---------------------------------------------------------------------

def summarize_day(all_meals: List[List[Dict]]) -> Dict:
    day_total = {"cal": 0, "protein": 0, "carbs": 0, "fat": 0}
    unknown = []

    for meal in all_meals:
        result = analyze_meal(meal)
        t = result["totals"]

        day_total["cal"] += t["cal"]
        day_total["protein"] += t["protein"]
        day_total["carbs"] += t["carbs"]
        day_total["fat"] += t["fat"]

        unknown.extend(result["unknown_items"])

    return {
        "day_totals": day_total,
        "unknown_items": list(set(unknown)),  # unique
    }


# ---------------------------------------------------------------------
# 3) HYDRATION RECOMMENDATION
# ---------------------------------------------------------------------

def hydration_recommendation(weight_kg: float, temperature_c: float = 25) -> float:
    """35 mL/kg baseline, scaled up for heat."""
    base = weight_kg * 0.035

    if temperature_c >= 32:
        base *= 1.20
    elif temperature_c >= 28:
        base *= 1.10

    return round(base, 2)


# ---------------------------------------------------------------------
# 4) DEFICIENCY PATTERN DETECTION (weekly)
# weekly_logs = [{"protein":..., "carbs":..., "fat":...}, ...]
# ---------------------------------------------------------------------

def detect_deficiencies(weekly_logs: List[Dict]) -> Dict:
    if not weekly_logs:
        return {"error": "No nutrition data"}

    protein_avg = sum(d.get("protein", 0) for d in weekly_logs) / len(weekly_logs)
    carb_avg = sum(d.get("carbs", 0) for d in weekly_logs) / len(weekly_logs)
    fat_avg = sum(d.get("fat", 0) for d in weekly_logs) / len(weekly_logs)

    flags = {
        "low_protein": protein_avg < 55,
        "low_carbs": carb_avg < 150,
        "low_healthy_fats": fat_avg < 40,
    }

    return {
        "weekly_avg": {
            "protein": round(protein_avg, 1),
            "carbs": round(carb_avg, 1),
            "fat": round(fat_avg, 1),
        },
        "flags": flags,
    }


# ---------------------------------------------------------------------
# 5) SIMPLE RULE-BASED MEAL PLAN
# ---------------------------------------------------------------------

def generate_meal_plan(user: Dict) -> Dict:
    goal = user.get("goal", "balanced")
    veg = user.get("vegetarian", False)

    if goal == "fat_loss":
        breakfast = ["oats", "apple"]
        lunch = ["dal", "roti (1 medium)"]
        dinner = ["roti (1 medium)", "vegetables"]

    elif goal == "muscle_gain":
        breakfast = ["oats", "milk"]
        lunch = ["rice cooked (1 cup)", "dal", "paneer"] if veg else ["rice cooked (1 cup)", "chicken"]
        dinner = ["paneer"] if veg else ["chicken"]

    else:  # balanced
        breakfast = ["banana", "milk"]
        lunch = ["rice cooked (1 cup)", "dal"]
        dinner = ["roti (1 medium)", "vegetables"]

    return {
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
    }


# ---------------------------------------------------------------------
# END OF MODULE
# ---------------------------------------------------------------------
