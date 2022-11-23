import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import plotly.express as px
import plotly.graph_objects as go
from inspect import getmembers, isfunction

px_list = getmembers(px, isfunction)
#go_list = getmembers(go, isclass)
chartOpts = ['px.'+i for i, y in px_list]#+['go.'+i for i, y in go_list]

preload = {"carshare":px.data.carshare(),
    "election":px.data.election(),
    "experiment":px.data.experiment(),
    "gapminder":px.data.gapminder(),
    "iris":px.data.iris(),
    "medals_wide":px.data.medals_wide(),
    "medals_long":px.data.medals_long(),
    "stocks":px.data.stocks(),
    "tips":px.data.tips(),
    "wind":px.data.wind()}

offCanvStyle = {'borderRadius':'15px'}



def layout():
    return [
        dbc.Offcanvas(['Select the chart type and options below',
            dcc.Dropdown(id={'type':'selectChart', 'index':'design'}, options=chartOpts),
            dmc.Accordion(id={'type':'graphingOptions', 'index':'design'}, value="chartOptions"),
            dbc.Button('Make Changes', id={'type': 'submitEdits', 'index': 'design'},
                       className='m-3'),
            ], id='chartEditor', style=offCanvStyle),
            dbc.Offcanvas(id='functions', children=[html.Div(id='functionHelper')], style=offCanvStyle),
            dbc.Button(id='openEditor', children='Edit Chart Details', n_clicks=0, className="me-1",
            style={'marginLeft': '1%'}),
            dbc.Button(id='openErrors', children='Toggle Errors', n_clicks=0, color="danger",
            style={'float': 'right', 'display': 'none', 'marginRight': '2%'}, className="me-1"),
            dbc.Button(id='openHelper', children='Show Function', n_clicks=0, color="info", className="me-1"),
            html.Div(id='errorsCanvas', children=[html.Pre(id='errors')]),
            html.Div([dcc.Graph(id='testFigure')], id='page-content')
    ]

dash.register_page('Data and Chart Explorer', path='/', layout=layout)

