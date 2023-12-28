from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from fastapi.middleware.wsgi import WSGIMiddleware
from dash.dependencies import Input, Output
import pandas as pd

class EnergyPlotter:
    def __init__(self, data_file):
        self.data = pd.read_csv(data_file)
        self.dash_app = Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        self.dash_app.layout = html.Div([
            dcc.RadioItems(
                id='options',
                options=[{'label': i, 'value': i} for i in ['Generation', '$Generation', 'Consumption', '$Consumption', 'Net', '$Net']],
                value='Generation',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id='graph')
        ])

    def setup_callbacks(self):
        @self.dash_app.callback(
            Output('graph', 'figure'),
            [Input('options', 'value')]
        )
        def update_graph(selected_option):
            hourly_data = self.data  # Assuming 'data' is an instance of EnergyData
            fig = go.Figure()

            fig.add_trace(go.Scatter(x=hourly_data['Datetime'], y=hourly_data[selected_option],
                                mode='lines', name=selected_option,
                                line=dict(color='lightgreen')))

            fig.update_layout(
                title='SDGE Data with EV TOU5 Rate',
                yaxis=dict(title='kWh' if '$' not in selected_option else '$'),
            )

            return fig

app = FastAPI()
# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
plotter = EnergyPlotter('docs/processed_data.csv')

# Serve Dash layout
@app.get("/")
def read_root():
    return HTMLResponse(plotter.dash_app.index())

app.mount("/plotter", WSGIMiddleware(plotter.dash_app.server))