import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from pages.home import offCanvStyle, chartOpts, acc

def layout():
    return html.Div([
                     html.Div(id='design-area', children=[], style={'backgroundColor':'#c5c6d0',
                                                       'position':'absolute', 'height':'100%',
                                                       'width':'100%'}),
                    dcc.Graph(id='testFigure', style={'display':'none'}),
                    dcc.Store(id='focused-graph', storage_type='local'),
                    dcc.Store(id='figures', storage_type='local', data=[]),
                     dbc.Offcanvas(['Select the chart type and options below',
                                    dcc.Dropdown(id={'index':'edit', 'type':'selectChart_edit'}, options=chartOpts),
                                    dbc.Button('Make Changes', id={'index':'edit', 'type':'submitEdits_edit'}),
                                    acc(id={'index':'edit','type':'graphingOptions_edit'}),
                                    ], id='chartDesignEditor', style=offCanvStyle),
                    dbc.Offcanvas(['Select the chart type and options below',
                                   dcc.Dropdown(id={'index': '2', 'type': 'selectChart_edit'}, options=chartOpts),
                                   dbc.Button('Make Changes', id={'index': '2', 'type': 'submitEdits_edit'}),
                                   acc(id={'index': '2', 'type': 'graphingOptions_edit'}),
                                   ], id='chartDesignEditor_edit', style=offCanvStyle),
                    html.Div([
                    dbc.Button('Toggle Edit Mode', id='toggleEdit', color="warning", className="me-1", n_clicks=0),
                    dbc.Button(id='openDesignEditor', children='Add Chart', n_clicks=0, className="me-1"),
                    dbc.Button(id='saveLayout', children='Save Layout', n_clicks=0, className="me-1", color='success'),
                        ], style={'zIndex':'1', 'position':'absolute', 'width':'100%'}),
                    dbc.Button(id='editActive', style={'display':'none'}),
                    dbc.Button(id='syncStore', style={'display': 'none'}),
                    dbc.Button(id='deleteTarget', style={'display': 'none'}),
                    ], id='design-holder')

dash.register_page('Designer', path='/designer', layout=layout)
