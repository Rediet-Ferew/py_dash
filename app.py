import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import time  # Simulate loading time
from crm_script import monthly_breakdown
from salesforce_data import get_dataframe, get_data

# Function to load data
def load_data():
    results = get_data()
    df = get_dataframe(results)
    data = monthly_breakdown(df)
    return data

# Initial Data Load
data = load_data()
monthly_df = data['monthly_breakdown']
monthly_df['month'] = monthly_df['month'].astype(str)

metrics = {
    "Basic LTV": data['Basic LTV'],
    "Advanced LTV": data['Advanced LTV'],
    "Average Purchase Value": data['Average Purchase Value'],
    "Average Purchase Frequency": data['Average Purchase Frequency'],
    "Average Customer Lifespan (Months)": data['Average Customer LifeSpan(Months)']
}
metrics_df = pd.DataFrame(metrics.items(), columns=["Metric", "Value"])
metrics_df["Value"] = metrics_df["Value"].round(2).astype(str)

dropdown_options = [{"label": col.replace("_", " ").title(), "value": col} for col in monthly_df.columns if col != "month"]

# Dash app setup
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Customer Insights"

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    html.Div([
        dcc.Link('📊 Static Dashboard', href='/'),
        " | ",
        dcc.Link('📈 Compare Two Features', href='/dynamic'),
        " | ",
        dcc.Link('📑 LTV and Key Metrics', href='/metrics'),
        " | ",
        html.Button("🔄 Refresh Data", id="refresh-btn", n_clicks=0),
    ], style={'padding': '10px', 'fontSize': '20px'}),

    html.Div(id="refresh-status", style={"color": "blue", "fontSize": "18px", "marginTop": "10px"}),  # Loading Message
    
    html.Div(id='page-content')  # Page Content
])

# Function to generate page layouts dynamically
def get_insights_layout():
    return html.Div([
        html.H1("CRM Analysis Report (Static)"),
        html.H2("Monthly Breakdown"),
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in monthly_df.columns],
            data=monthly_df.round(2).astype(str).to_dict('records'),
            style_table={'overflowX': 'auto'}
        ),
        html.H2("Insights"),
        dcc.Graph(figure=px.line(monthly_df, x='month', y=['new_customers', 'returning_customers'],
                                 title="New vs Returning Customers Trend", markers=True)),
        dcc.Graph(figure=px.line(monthly_df, x='month', y=['new_percentage', 'returning_percentage'],
                                 title="New vs Returning Customers Percentage Trend", markers=True)),
        dcc.Graph(figure=px.bar(monthly_df, x='month', y=['total_revenue', 'new_customer_revenue', 'returning_customer_revenue'],
                                 title="Revenue Breakdown", barmode='group')),
        dcc.Graph(figure=px.bar(monthly_df, x='month', y=['new_customer_revenue', 'returning_customer_revenue'],
                                 title="New Customer Revenue vs Returning Customer Revenue", barmode='group')),
    ])

def get_dynamic_graph_layout():
    return html.Div([
        html.H1("📈 Compare Two Features Over Month"),
        html.Label("Select First Feature:"),
        dcc.Dropdown(id='y-axis-dropdown-1', options=dropdown_options, value='new_customers', clearable=False),
        html.Label("Select Second Feature:"),
        dcc.Dropdown(id='y-axis-dropdown-2', options=dropdown_options, value='returning_customers', clearable=False),
        dcc.Graph(id='dynamic-comparison-graph')
    ])

def get_metrics_layout():
    return html.Div([
        html.H1("Key Metrics"),
        dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in metrics_df.columns],
            data=metrics_df.to_dict('records'),
            style_table={'overflowX': 'auto'}
        ),
    ])

# Combined Callback for Page Navigation & Refresh Button
@app.callback(
    [Output('page-content', 'children'),
     Output('refresh-status', 'children'),
     Output("refresh-btn", "children")],  # Updates button text
    [Input('url', 'pathname'), Input('refresh-btn', 'n_clicks')],
    prevent_initial_call=True
)
def update_page(pathname, n_clicks):
    """ Handles both page navigation and refresh button with a loading state """
    global data, monthly_df, metrics_df  

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'refresh-btn.n_clicks':
        # Show "Refreshing..." Message
        return dash.no_update, "🕛 Refreshing data... Please wait.", "Refreshing..."

    # Handle page routing
    if pathname == '/dynamic':
        return get_dynamic_graph_layout(), "", "🔄 Refresh Data"
    elif pathname == '/metrics':
        return get_metrics_layout(), "", "🔄 Refresh Data"
    return get_insights_layout(), "", "🔄 Refresh Data"

# Callback to actually refresh data after some delay
@app.callback(
    [Output('page-content', 'children', allow_duplicate=True),
     Output('refresh-status', 'children', allow_duplicate=True),
     Output("refresh-btn", "children", allow_duplicate=True)],
    Input("refresh-btn", "n_clicks"),
    State('url', 'pathname'),
    prevent_initial_call="initial_duplicate"
)
def refresh_dashboard(n_clicks, pathname):
    """ Simulates data reloading and updates the UI with a success message """
    global data, monthly_df, metrics_df  

    # Simulating a loading delay (Replace this with actual data fetch)
    time.sleep(3)

    # Reload data
    data = load_data()
    monthly_df = data['monthly_breakdown']
    monthly_df['month'] = monthly_df['month'].astype(str)

    metrics = {
        "Basic LTV": data['Basic LTV'],
        "Advanced LTV": data['Advanced LTV'],
        "Average Purchase Value": data['Average Purchase Value'],
        "Average Purchase Frequency": data['Average Purchase Frequency'],
        "Average Customer Lifespan (Months)": data['Average Customer LifeSpan(Months)']
    }
    metrics_df = pd.DataFrame(metrics.items(), columns=["Metric", "Value"])
    metrics_df["Value"] = metrics_df["Value"].round(2).astype(str)

    # Determine which page to refresh
    if pathname == '/dynamic':
        page_layout = get_dynamic_graph_layout()
    elif pathname == '/metrics':
        page_layout = get_metrics_layout()
    else:
        page_layout = get_insights_layout()

    return page_layout, "✅ Data refreshed successfully!", "🔄 Refresh Data"

# Dynamic Graph Update Callback
@app.callback(
    Output('dynamic-comparison-graph', 'figure'),
    [Input('y-axis-dropdown-1', 'value'),
     Input('y-axis-dropdown-2', 'value')]
)
def update_graph(y_axis_1, y_axis_2):
    fig = px.line(monthly_df, x='month', y=[y_axis_1, y_axis_2], 
                  title=f"Comparison: {y_axis_1.replace('_', ' ').title()} vs {y_axis_2.replace('_', ' ').title()}",
                  markers=True)
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
