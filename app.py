import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from crm_script import monthly_breakdown

# Load the data
data = monthly_breakdown("crm_cleaned_data.csv")
monthly_df = data['monthly_breakdown']

# Convert month period to string for plotting
monthly_df['month'] = monthly_df['month'].astype(str)

metrics = {
    "Basic LTV": data['Basic LTV'],
    "Advanced LTV": data['Advanced LTV'],
    "Average Purchase Value": data['Average Purchase Value'],
    "Average Purchase Frequency": data['Average Purchase Frequency'],
    "Average Customer Lifespan (Months)": data['Average Customer LifeSpan(Months)']
}
metrics_df = pd.DataFrame(metrics.items(), columns=["Metric", "Value"])

# Available columns for dropdown selection (excluding "month")
dropdown_options = [{"label": col.replace("_", " ").title(), "value": col} for col in monthly_df.columns if col != "month"]

# Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Customer Insights"

# Layout for Navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Stores the current page
    html.Div([
        dcc.Link('📊 Static Dashboard', href='/'),
        " | ",
        dcc.Link('📈 Compare Two Features', href='/dynamic'),
        " | ",
        dcc.Link('📑 LTV and Key Metrics', href='/metrics'),
    ], style={'padding': '10px', 'fontSize': '20px'}),

    html.Div(id='page-content')  # Content updates based on the selected page
])

# ====== PAGE 1: Insights Dashboard ======
insights_layout = html.Div([
    html.H1("CRM Analysis Report(Static)"),
    
    # Monthly Breakdown Table
    html.H2("Monthly Breakdown"),
    dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in monthly_df.columns],
        data=monthly_df.round(2).astype(str).to_dict('records'),
        style_table={'overflowX': 'auto'}
    ),
    
    # Graphs
    html.H2("Insights"),
    
    # New vs. Returning Customers (Line Graph)
    dcc.Graph(
        figure=px.line(
            monthly_df, x='month', y=['new_customers', 'returning_customers'],
            title="New vs Returning Customers Trend", markers=True
        )
    ),
    
    # New vs Returning Customers Percentage (Line Graph)
    dcc.Graph(
        figure=px.line(
            monthly_df, x='month', y=['new_percentage', 'returning_percentage'],
            title="New vs Returning Customers Percentage Trend", markers=True
        )
    ),
    
    # Revenue Breakdown (Bar Graph)
    dcc.Graph(
        figure=px.bar(monthly_df, x='month', y=['total_revenue', 'new_customer_revenue', 'returning_customer_revenue'],
                       title="Revenue Breakdown", barmode='group')
    ),
    
    # New vs Returning Revenue (Bar Graph)
    dcc.Graph(
        figure=px.bar(monthly_df, x='month', y=['new_customer_revenue', 'returning_customer_revenue'],
                       title="New Customer Revenue vs Returning Customer Revenue", barmode='group')
    ),
    
])

# ====== PAGE 2: Dynamic Comparison Graph ======
dynamic_graph_layout = html.Div([
    html.H1("📈 Compare Two Features Over Month"),
    
    html.Label("Select First Feature:"),
    dcc.Dropdown(
        id='y-axis-dropdown-1',
        options=dropdown_options,
        value='new_customers',  # Default Y-axis 1
        clearable=False
    ),
    
    html.Label("Select Second Feature:"),
    dcc.Dropdown(
        id='y-axis-dropdown-2',
        options=dropdown_options,
        value='returning_customers',  # Default Y-axis 2
        clearable=False
    ),
    
    dcc.Graph(id='dynamic-comparison-graph')
])

metrics_df["Value"] = metrics_df["Value"].round(2).astype(str)

metrics_layout = html.Div([
    html.H1("Key Metrics"),
    
    dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in metrics_df.columns],
        data=metrics_df.to_dict('records'),
        style_table={'overflowX': 'auto'}
    ),
])
# ====== CALLBACKS ======

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """ Update the displayed page based on navigation. """
    if pathname == '/dynamic':
        return dynamic_graph_layout
    elif pathname == '/metrics':
        return metrics_layout
    return insights_layout  # Default page

@app.callback(
    Output('dynamic-comparison-graph', 'figure'),
    [Input('y-axis-dropdown-1', 'value'),
     Input('y-axis-dropdown-2', 'value')]
)
def update_graph(y_axis_1, y_axis_2):
    """ Update the dynamic graph with two selected features (Y-axis). """
    fig = px.line(monthly_df, x='month', y=[y_axis_1, y_axis_2], 
                  title=f"Comparison: {y_axis_1.replace('_', ' ').title()} vs {y_axis_2.replace('_', ' ').title()}",
                  markers=True)
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
