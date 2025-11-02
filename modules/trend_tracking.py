import pandas as pd
import plotly.express as px
import json
from datetime import datetime

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
    Display time trends for Lifestyle Score, BMI, Sleep, and Activity.
    """
    if df.empty:
        print("No data to visualize progress.")
        return

    # Ensure consistent datatypes
    df['Lifestyle_score'] = pd.to_numeric(df.get('Lifestyle_score', 0), errors='coerce')
    df['BMI'] = pd.to_numeric(df.get('BMI', 0), errors='coerce')
    df['Sleep_hours_per_night'] = pd.to_numeric(df.get('Sleep_hours_per_night', 0), errors='coerce')
    df['Physical_Activity_min_per_week'] = pd.to_numeric(df.get('Physical_Activity_min_per_week', 0), errors='coerce')

    # Melt into long form for easier multi-line plotting
    plot_df = df[['Timestamp','Lifestyle_score','BMI','Sleep_hours_per_night','Physical_Activity_min_per_week']] \
        .rename(columns={
            'Lifestyle_score': 'Lifestyle Score',
            'BMI': 'BMI',
            'Sleep_hours_per_night': 'Sleep (h/night)',
            'Physical_Activity_min_per_week': 'Exercise (min/wk)'
        })
    plot_df = plot_df.melt(id_vars='Timestamp', var_name='Metric', value_name='Value')

    fig = px.line(
        plot_df,
        x='Timestamp', y='Value', color='Metric',
        markers=True,
        title='Health & Lifestyle Progress Over Time',
        template='plotly_white'
    )
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        legend_title_text='Metric',
        xaxis_title='Date',
        yaxis_title='Value',
        hovermode='x unified',
        height=500
    )
    fig.show()

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
        'Physical_Activity_min_per_week': 'mean',
        'Sleep_hours_per_night': 'mean'
    }).round(2)

    print("\n--- Weekly Health Summary ---")
    print(summary.tail(5))
    return summary
