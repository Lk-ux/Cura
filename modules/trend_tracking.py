import pandas as pd
import plotly.express as px
import json
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# =========================================
# MODULE 5: Trend Tracking
# =========================================
def load_history(filename="health_history.json"):
    """
    Load all saved health/lifestyle records.
    Returns a pandas DataFrame with timestamp parsing.
    """
    try:
        with open(filename, 'r') as f:
            all_data = json.load(f)
        records = []
        for r in all_data:
            row = {**r['data'], **r['metrics']}
            # Add timestamp (use current time if not stored)
            row['Timestamp'] = r.get('timestamp', datetime.now().isoformat())
            records.append(row)
        df = pd.DataFrame(records)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df.sort_values('Timestamp', inplace=True)
        return df
    except FileNotFoundError:
        print("No previous health data found.")
        return pd.DataFrame()


# =========================================
# MODULE 5A: Trend Plotting
# =========================================
def plot_progress(df):
    """
    Display multi-metric trends for health & lifestyle data.
    Metrics: Lifestyle Score, BMI, Sleep, Physical Activity, Diet, Water, Stress, Screen hours, CVD risk.
    """
    if df.empty:
        print("No data to visualize progress.")
        return

    # Ensure numeric types
    metrics_to_numeric = [
        'Lifestyle_score', 'BMI', 'Sleep_hours_per_night', 'Physical_Activity_min_per_week',
        'Diet_FV_servings_avg', 'Water_glasses', 'Stress_level', 'Screen_hours', 'CVD_risk'
    ]
    for col in metrics_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df.get(col, 0), errors='coerce')

    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=("Vitals & Body Metrics", "Lifestyle & Daily Habits", "Risk & Scores")
    )

    # --- Row 1: Vitals & Body ---
    if 'BMI' in df.columns:
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['BMI'], mode='lines+markers', name='BMI'), row=1, col=1)
        # healthy BMI band
        fig.add_hrect(y0=18.5, y1=24.9, fillcolor="green", opacity=0.1, line_width=0, row=1, col=1)

    # --- Row 2: Lifestyle & Daily Habits ---
    lifestyle_metrics = {
        'Sleep_hours_per_night': ('Sleep (h/night)', 7, 9),
        'Physical_Activity_min_per_week': ('Exercise (min/wk)', 150, None),
        'Diet_FV_servings_avg': ('Fruits+Veg (servings/day)', 5, None),
        'Water_glasses': ('Water intake (glasses/day)', 8, None),
        'Stress_level': ('Stress level', 0, 5),
        'Screen_hours': ('Screen hours/day', 0, 8)
    }
    for col, (label, low, high) in lifestyle_metrics.items():
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df['Timestamp'], y=df[col], mode='lines+markers', name=label), row=2, col=1)
            if low is not None and high is not None:
                fig.add_hrect(y0=low, y1=high, fillcolor="green", opacity=0.05, line_width=0, row=2, col=1)

    # --- Row 3: Risk & Scores ---
    if 'Lifestyle_score' in df.columns:
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Lifestyle_score'], mode='lines+markers', name='Lifestyle Score'), row=3, col=1)
    if 'CVD_risk' in df.columns:
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['CVD_risk'], mode='lines+markers', name='Estimated CVD Risk'), row=3, col=1)
        fig.add_hrect(y0=0, y1=5, fillcolor="green", opacity=0.05, line_width=0, row=3, col=1)
        fig.add_hrect(y0=20, y1=100, fillcolor="red", opacity=0.05, line_width=0, row=3, col=1)

    # Layout
    fig.update_layout(
        height=900, width=1000,
        title_text="Health & Lifestyle Progress Over Time",
        hovermode="x unified",
        template="plotly_white"
    )
    fig.update_xaxes(title_text="Date")
    fig.show(renderer="browser")



# =========================================
# MODULE 5B: Weekly Summary
# =========================================
def weekly_summary(df):
    """
    Prints and returns weekly averages for main health metrics.
    """
    if df.empty:
        print("No data available for weekly summary.")
        return

    df['Week'] = df['Timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
    summary = df.groupby('Week').agg({
        'Lifestyle_score': 'mean',
        'BMI': 'mean',
        'Physical_activity_min': lambda x: x.mean() * 7,
        'Sleep_hours_avg': 'mean'
    }).round(2)

    print("\n--- Weekly Health Summary ---")
    print(summary.tail(5))
    return summary
