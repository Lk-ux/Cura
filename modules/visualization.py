import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import plotly.io as pio

pio.renderers.default = 'browser'  # safer cross-environment default


def plot_health_dashboard(data, metrics):
    """
    Combines lifestyle visualization + CVD risk gauge
    into one cohesive interactive dashboard.
    """

    # -----------------------------
    # Normalize lifestyle factors
    # -----------------------------
    factors = {
        'Exercise': min(data.get('Physical_Activity_min_per_week', 0) / 150, 1),
        'Sleep': 1 if 7 <= data.get('Sleep_hours_per_night', 0) <= 9 else 0.5,
        'Fruits': min(data.get('Fruits_per_day', 0) / 5, 1),
        'Vegetables': min(data.get('Vegetables_per_day', 0) / 5, 1),
        'Smoking': 1 if data.get('Cigarettes_per_day', 0) == 0 else 0,
        'Alcohol': 1 if data.get('Alcohol_units_per_week', 0) <= 7 else 0.5,
        'Hydration': min(data.get('Water_glasses_per_day', 0) / 8, 1),
        'Stress': 1 - (data.get('Stress_level', 10) / 10),
        'Social': min(data.get('Social_interactions_per_week', 0) / 7, 1)
    }

    labels = list(factors.keys())
    values = list(factors.values())
    ideal_values = [1] * len(values)
    lifestyle_score = round(np.mean(values) * 100, 1)
    cvd_risk = metrics.get('CVD_risk', 0)

    # -----------------------------
    # Create combined subplots layout
    # -----------------------------
    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{'type': 'polar'}, {'type': 'bar'}, {'type': 'indicator'}]],
        column_widths=[0.35, 0.35, 0.3],
        subplot_titles=("Lifestyle Balance", "Component Strengths", "CVD Risk & Score")
    )

    # --- Radar Chart ---
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill='toself',
            name='Your Profile',
            line=dict(color='teal', width=2)
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatterpolar(
            r=ideal_values + [ideal_values[0]],
            theta=labels + [labels[0]],
            fill='toself',
            name='Optimal',
            line=dict(color='lightgray', dash='dot'),
            opacity=0.3
        ),
        row=1, col=1
    )

    # --- Bar Chart ---
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            marker=dict(
                color=values,
                colorscale='Viridis',
                cmin=0, cmax=1
            ),
            text=[f"{v*100:.0f}%" for v in values],
            textposition="outside",
        ),
        row=1, col=2
    )

    # --- Combined Gauge: Lifestyle + CVD ---
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=lifestyle_score,
            number={'suffix': ' / 100', 'font': {'size': 18}},
            delta={'reference': 70, 'increasing': {'color': "green"}},
            title={'text': "Lifestyle Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "teal"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffcccc"},
                    {'range': [50, 75], 'color': "#fff3cd"},
                    {'range': [75, 100], 'color': "#ccffcc"},
                ]
            },
            domain={'x': [0.68, 1], 'y': [0.55, 1]}
        ),
        row=1, col=3
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=cvd_risk,
            number={'suffix': '%', 'font': {'size': 18}},
            title={'text': "Predicted CVD Risk"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "crimson"},
                'steps': [
                    {'range': [0, 10], 'color': '#90EE90'},
                    {'range': [10, 20], 'color': '#FFD700'},
                    {'range': [20, 100], 'color': '#FF6347'}
                ],
            },
            domain={'x': [0.68, 1], 'y': [0, 0.45]}
        ),
        row=1, col=3
    )

    # -----------------------------
    # Layout aesthetics
    # -----------------------------
    fig.update_layout(
        title={'text': "Comprehensive Health Dashboard", 'x': 0.5},
        showlegend=False,
        template='plotly_white',
        height=600,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        )
    )

    fig.show(renderer="browser")

