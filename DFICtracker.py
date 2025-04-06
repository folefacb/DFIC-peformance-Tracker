import pandas as pd
import plotly.graph_objects as go

# Load data
url = "https://raw.githubusercontent.com/folefacb/DFIC-peformance-Tracker/refs/heads/main/performance_data_2025-04-05.csv"
df = pd.read_csv(url)
df['date'] = pd.to_datetime(df['date'])

# Columns to plot
return_cols = ['inception_return', 'one_day_return', 'one_week_return', 'one_month_return', 'one_year_return']

# Convert return columns to numeric (coerce '-' or invalid to NaN)
for col in return_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop rows where all return columns are NaN
df.dropna(subset=return_cols, how='all', inplace=True)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("DFIC Return Performance Dashboard"),

    html.Label("Select Return Types:"),
    dcc.Checklist(
        id='return-selector',
        options=[{'label': col, 'value': col} for col in return_cols],
        value=return_cols,
        inline=True
    ),

    dcc.Graph(id='returns-scatter-plot')
])

@app.callback(
    Output('returns-scatter-plot', 'figure'),
    Input('return-selector', 'value')
)
def update_graph(selected_returns):
    fig = go.Figure()

    for col in selected_returns:
        # Filter out rows with NaN in this column
        df_filtered = df[['date', col]].dropna()

        # Color logic: red = up from previous, green = down or same
        color = ['red' if later > now else 'green'
                 for now, later in zip(df_filtered[col], df_filtered[col].shift(-1))]

        # Pad color list to match length
        color.append(color[-1])  # Just duplicate last color for same length as points

        fig.add_trace(go.Scatter(
            x=df_filtered['date'],
            y=df_filtered[col],
            mode='markers+lines',
            marker=dict(color=color, size=8),
            name=col
        ))

    fig.update_layout(
        title="Return Over Time",
        xaxis_title="Date",
        yaxis_title="Return",
        legend_title="Return Type",
        hovermode='x unified'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
