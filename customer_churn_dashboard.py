# =========================================================================
# PERFECTED 16:9 HYBRID CHURN DASHBOARD (BARS + DONUTS WITH TOTAL VERIFICATION)
# =========================================================================

!pip install plotly -q

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------------------------------
# 1. Load & Clean Dataset
# -------------------------------------------------------------------------
df = pd.read_csv('/content/WA_Fn-UseC_-Telco-Customer-Churn.csv')

# Enterprise data cleaning pipeline
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
df['SeniorCitizen'] = df['SeniorCitizen'].map({1: 'Yes', 0: 'No'})
df = df.replace('No internet service', 'No')
df = df.replace('No phone service', 'No')

# -------------------------------------------------------------------------
# 2. Executive Metric Calculations
# -------------------------------------------------------------------------
total_customers = len(df)
churn_customers = len(df[df['Churn'] == 'Yes'])
active_customers = len(df[df['Churn'] == 'No'])
churn_rate = round((churn_customers / total_customers) * 100, 2)
total_revenue_m = round(df['TotalCharges'].sum() / 1000000, 2)
revenue_lost = round(
    df[df['Churn']=='Yes']['TotalCharges'].sum()/1000000,2
)

# -------------------------------------------------------------------------
# 3. Data Transformations & Percentage Label Splicing
# -------------------------------------------------------------------------
def process_segment(dataframe, column_name):
    grouped = dataframe.groupby([column_name, 'Churn'], observed=False).size().unstack(fill_value=0).reset_index()
    grouped['Total'] = grouped['Yes'] + grouped['No']
    grouped['No_Pct'] = (grouped['No'] / grouped['Total'] * 100).round(1).astype(str) + '%'
    grouped['Yes_Pct'] = (grouped['Yes'] / grouped['Total'] * 100).round(1).astype(str) + '%'
    grouped['No_Label'] = grouped['No'].map('{:,}'.format) + " (" + grouped['No_Pct'] + ")"
    grouped['Yes_Label'] = grouped['Yes'].map('{:,}'.format) + " (" + grouped['Yes_Pct'] + ")"
    return grouped

contract_data = process_segment(df, 'Contract').sort_values(by='Total', ascending=False)

df['TenureGroup'] = pd.cut(df['tenure'], bins=[0, 12, 24, 48, 72], labels=['0-1 Year', '1-2 Years', '2-4 Years', '4+ Years'])
tenure_data = process_segment(df, 'TenureGroup')
payment_data = process_segment(df,'PaymentMethod')
senior_data = process_segment(df,'SeniorCitizen')
senior_labels = {
    'Yes': 'Senior Citizen',
    'No': 'Non-Senior Citizen'
}

senior_data['SeniorCitizen'] = senior_data['SeniorCitizen'].map(senior_labels)

tech_data = process_segment(df,'TechSupport')

security_data = process_segment(df,'OnlineSecurity')
security_labels = {
    'Yes': 'Security Enabled',
    'No': 'No Security'
}

security_data['OnlineSecurity'] = security_data['OnlineSecurity'].map(security_labels)

# Pie segments mapping
internet_counts = df['InternetService'].value_counts()

# -------------------------------------------------------------------------
# 4. Premium Hybrid 16:9 Layout Mapping
# -------------------------------------------------------------------------
fig = make_subplots(
    rows=3,
    cols=4,

    row_heights=[0.18, 0.41, 0.41],

    column_widths=[0.25, 0.25, 0.25, 0.25],

    specs=[
        [
            {"type": "indicator"},
            {"type": "indicator"},
            {"type": "indicator"},
            {"type": "indicator"}
        ],

        [
            {"type": "bar"},
            {"type": "bar"},
            {"type": "pie"},
            {"type": "pie"}
        ],

        [
            {"type": "bar"},
            {"type": "pie"},
            {"type": "bar"},
            {"type": "pie"}
        ]
    ],

    subplot_titles=(

        "", "", "", "",

        "<b>Contract Length vs Churn</b>",
        "<b>Tenure Attrition Curve</b>",
        "<b>Overall Churn Ratio</b>",
        "<b>Internet Service Distribution</b>",

        "<b>Payment Method Analysis</b>",
        "<b>Senior Citizen Churn</b>",
        "<b>Customer Churn by Tech Support Availability</b>",
        "<b>Online Security Impact</b>"
    ),

    horizontal_spacing=0.05,
    vertical_spacing=0.12
)
# Core Theme Color Map
COLOR_RETAINED = "#1e40af"  # Deep Corporate Blue
COLOR_CHURNED  = "#ef4444"  # High-Alert Red
PIE_COLORS     = ["#1e40af", "#38bdf8", "#93c5fd"] # Blue tones for multi-class splits

# -------------------------------------------------------------------------
# 5. KPI Metrics Traces
# -------------------------------------------------------------------------
fig.add_trace(go.Indicator(
    mode="number", value=total_customers,
    number={'valueformat': ',', 'font': {'color': '#ffffff', 'size': 54, 'family': 'Arial', 'weight': 'bold'}},
    title={"text": "<span style='color:#94a3b8; font-size:13px; font-weight:bold; letter-spacing:1px;'>TOTAL PORTFOLIO USERS</span>"}
), row=1, col=1)

fig.add_trace(go.Indicator(
    mode="number", value=churn_rate,
    number={'suffix': '%', 'font': {'color': COLOR_CHURNED, 'size': 58, 'family': 'Arial', 'weight': 'bold'}},
    title={"text": "<span style='color:#94a3b8; font-size:13px; font-weight:bold; letter-spacing:1px;'>AGGREGATE CHURN VELOCITY</span>"}
), row=1, col=2)

fig.add_trace(go.Indicator(
    mode="number", value=total_revenue_m,
    number={'prefix': '$', 'suffix': ' M', 'font': {'color': '#10b981', 'size': 54, 'family': 'Arial', 'weight': 'bold'}},
    title={"text": "<span style='color:#94a3b8; font-size:13px; font-weight:bold; letter-spacing:1px;'>EVALUATED GROSS REVENUE</span>"}
), row=1, col=3)

fig.add_trace(
    go.Indicator(
        mode="number",
        value=revenue_lost,
        number={
            'prefix':'$',
            'suffix':' M',
            'font':{
                'size':54,
                'color':'#f59e0b'
            }
        },
        title={
            "text":"<span style='color:#94a3b8;font-size:13px;'>REVENUE LOST</span>"
        }
    ),
    row=1,
    col=4
)

# -------------------------------------------------------------------------
# 6. Advanced Stacked Bar Traces (Left Side)
# -------------------------------------------------------------------------
# Chart A: Contract Mix
fig.add_trace(go.Bar(x=contract_data['Contract'], y=contract_data['No'], hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',text=contract_data['No_Label'], textposition='inside', insidetextanchor='middle', name='Retained', marker_color=COLOR_RETAINED, showlegend=True, textfont=dict(size=11, color='white', weight='bold')), row=2, col=1)
fig.add_trace(go.Bar(x=contract_data['Contract'], y=contract_data['Yes'], hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',text=contract_data['Yes_Label'], textposition='inside', insidetextanchor='middle', name='Churned', marker_color=COLOR_CHURNED, showlegend=True, textfont=dict(size=11, color='white', weight='bold')), row=2, col=1)

# Chart B: Tenure Blocks
fig.add_trace(go.Bar(x=tenure_data['TenureGroup'], y=tenure_data['No'], hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',text=tenure_data['No_Label'], textposition='inside', insidetextanchor='middle', marker_color=COLOR_RETAINED, showlegend=False, textfont=dict(size=11, color='white', weight='bold')), row=2, col=2)
fig.add_trace(go.Bar(x=tenure_data['TenureGroup'], y=tenure_data['Yes'], text=tenure_data['Yes_Label'], textposition='inside', insidetextanchor='middle', marker_color=COLOR_CHURNED, showlegend=False, textfont=dict(size=11, color='white', weight='bold')), row=2, col=2)

# Chart C: 
fig.add_trace(
    go.Bar(
        x=payment_data['PaymentMethod'],
        y=payment_data['No'],
        hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
        marker_color=COLOR_RETAINED,
        name='Retained',
        showlegend=False
    ),
    row=3,col=1
)

fig.add_trace(
    go.Bar(
        x=payment_data['PaymentMethod'],
        y=payment_data['Yes'],
        hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
        marker_color=COLOR_CHURNED,
        name='Churned',
        showlegend=False
    ),
    row=3,col=1
)

# Chart D: 
fig.add_trace(
    go.Bar(
        x=tech_data['TechSupport'],
        y=tech_data['No'],
        hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
        marker_color=COLOR_RETAINED,
        name='Retained',
        showlegend=False,
    ),
    row=3,col=3
)

fig.add_trace(
    go.Bar(
        x=tech_data['TechSupport'],
        y=tech_data['Yes'],
        hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
        marker_color=COLOR_CHURNED,
        name='Churned',
        showlegend=False
    ),
    row=3,col=3
)
# -------------------------------------------------------------------------
# 7. High-Contrast Donut Chart Traces (Right Side)
# -------------------------------------------------------------------------
# Chart E: Overall Customer Attrition Donut
fig.add_trace(go.Pie(
    labels=['Retained', 'Churned'], 
    values=[active_customers, churn_customers],
    hole=0.6,
    marker=dict(colors=[COLOR_RETAINED, COLOR_CHURNED]),
    textinfo='label+percent',
    textfont=dict(size=12, weight='bold', color='white'),
    showlegend=False,
    hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
), row=2, col=3)

# Chart F: Internet Product Distribution Donut
fig.add_trace(go.Pie(
    labels=internet_counts.index, 
    values=internet_counts.values,
    hole=0.6,
    marker=dict(colors=PIE_COLORS),
    textinfo='label+percent',
    textfont=dict(size=11, weight='bold', color='white'),
    showlegend=False,
    hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
), row=2, col=4)

# Chart G:
fig.add_trace(
    go.Pie(
        labels=senior_data['SeniorCitizen'],
        values=senior_data['Yes'],
        hole=0.6,
        textinfo='label+percent',
        showlegend=False,
        hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
    ),
    row=3,col=2
)

# Chart H:
fig.add_trace(
    go.Pie(
        labels=security_data['OnlineSecurity'],
        values=security_data['Yes'],
        hole=0.6,
        textinfo='label+percent',
        showlegend=False,
        hovertemplate=
        '<b>%{x}</b><br>' +
        'Retained: %{y}<extra></extra>',
    ),
    row=3,col=4
)

# -------------------------------------------------------------------------
# 8. Canvas Formatting & Visual Polish
# -------------------------------------------------------------------------
fig.update_layout(
    height=1400,
    width=1600,
    barmode='stack',
    template="plotly_dark",

    paper_bgcolor="#090d16",
    plot_bgcolor="#111827",

    title={
        'text': "<b>TELCO CUSTOMER CHURN & RETENTION INTELLIGENCE DASHBOARD</b><br><span style='font-size:13px; color:#64748b;'>Customer Attrition Analysis | Revenue Impact | Retention Drivers</span>",
        'y': 0.95,
        'x': 0.04,
        'xanchor': 'left',
        'yanchor': 'top'
    },

    font=dict(
        family="Arial",
        size=11,
        color="#cbd5e1"
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0.84,
        xanchor="center",
        x=0.5
    ),

    margin=dict(
        t=150,
        b=180,
        l=50,
        r=50
    )
)

# Clean and normalize axes lines only on the bar charts (cols 1 and 2)
for r,c in [(2,1),(2,2),(3,1),(3,3)]:
    fig.update_xaxes(
        tickangle=-20,
        row=3,
        col=1
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1f2937",
        row=r,
        col=c
    )
# Render inside Google Colab cell
fig.show()

# Export clean portfolio HTML file
fig.write_html("Verified_Hybrid_Churn_Dashboard.html")
print("\n🎉 Success! Widescreen 'Verified_Hybrid_Churn_Dashboard.html' is fully cooked and ready to share.")
