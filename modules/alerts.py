from modules.trend_tracking import load_history

# =========================================
# Alert System for Declining Metrics
# =========================================
def check_for_decline(filename="health_data.json", metrics_to_check=None, threshold_pct=5):
    """
    Checks last two records for significant decline in key metrics.
    Alerts if decline exceeds threshold_pct (%).
    """
    if metrics_to_check is None:
        metrics_to_check = ['Lifestyle_score', 'BMI', 'Sleep_hours_per_night', 'Physical_Activity_min_per_week']

    df = load_history(filename)
    if df.shape[0] < 2:
        print("Not enough data for trend analysis.")
        return

    last_two = df.tail(2)
    alerts = []
    for metric in metrics_to_check:
        old_val = last_two.iloc[0].get(metric)
        new_val = last_two.iloc[1].get(metric)
        if old_val is None or new_val is None:
            continue

        # Percent change
        change_pct = ((new_val - old_val) / old_val) * 100 if old_val != 0 else 0

        # Trigger alert if negative change exceeds threshold
        if change_pct < -threshold_pct:
            alerts.append(f"⚠️ {metric} decreased by {abs(change_pct):.1f}% since last entry.")

    if alerts:
        print("\n--- Decline Alerts ---")
        for alert in alerts:
            print(alert)
    else:
        print("\nNo significant declines detected.")

    return alerts
