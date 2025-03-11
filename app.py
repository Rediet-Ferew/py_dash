import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd

# Load Iris dataset from local CSV file
df = pd.read_csv("Iris.csv", header=None)

# Assign column names
df.columns = ['Id','sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)', 'species']

# Create a Dash app
app = dash.Dash(__name__)
server = app.server
# Available columns for dropdown
columns = df.columns[:-1]

app.layout = html.Div([
    html.H1("Iris Dataset Dashboard", style={'textAlign': 'center'}),

    # Dropdowns for X and Y axis selection
    html.Label("Select X-axis:"),
    dcc.Dropdown(
        id='x-axis',
        options=[{'label': col, 'value': col} for col in columns],
        value='sepal length (cm)'
    ),
    
    html.Label("Select Y-axis:"),
    dcc.Dropdown(
        id='y-axis',
        options=[{'label': col, 'value': col} for col in columns],
        value='sepal width (cm)'
    ),

    # Scatter plot
    dcc.Graph(id='scatter-plot'),

    # Data Table
    dash_table.DataTable(
        id='iris-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.head(10).to_dict('records'),
        style_table={'margin': 'auto', 'width': '80%'}
    )
])

# Callback to update scatter plot based on dropdown selection
@app.callback(
    dash.Output('scatter-plot', 'figure'),
    [dash.Input('x-axis', 'value'),
     dash.Input('y-axis', 'value')]
)
def update_scatter(x_col, y_col):
    fig = px.scatter(df, x=x_col, y=y_col, color='species',
                     title=f"{x_col} vs {y_col}", height=500)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
