from dash import Dash, html, dcc, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
from inspect import getmembers, isfunction, getargvalues, signature, isclass
import dash_bootstrap_components as dbc
from dash_mantine_components import Accordion as acc
from utils.makeCharts import makeCharts, getOpts, parseSelections

import datetime, base64, io, pandas as pd

import plotly.express as px
import plotly.graph_objects as go

px_list = getmembers(px, isfunction)
#go_list = getmembers(go, isclass)
chartOpts = ['px.'+i for i, y in px_list]#+['go.'+i for i, y in go_list]



app = Dash(__name__, suppress_callback_exceptions=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           )

app.layout = html.Div(id='div-app',children=[
    dcc.Location(id='url'),
    dcc.Upload(id='uploadContent',
               children=html.Div([
                   'Drag and Drop or ',
                   html.A('Select Files')
               ]),
               style={
                   'width': '100%',
                   'height': '60px',
                   'lineHeight': '60px',
                   'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'borderRadius': '5px',
                   'textAlign': 'center',
                   'margin': '10px'
               },
                # Allow multiple files to be uploaded
                multiple=True
               ),
    html.Div(id='contentDisplay', style={'maxHeight':'25vh', 'overflowY':'auto'}),
    dbc.Offcanvas(['Select the chart type and options below',
                   dcc.Dropdown(id='selectChart', options=chartOpts),
                   dbc.Button('Make Changes', id='submitEdits'),
                   acc(id='graphingOptions'),
                   ], id='chartEditor'),
    dbc.Offcanvas(id='errors'),
    dbc.Offcanvas(id='functions', children=[html.Pre(id='functionHelper')]),
    dbc.Button(id='openEditor', children='Edit Chart Details', n_clicks=0, className="me-1"),
    dbc.Button(id='openErrors', children='Show Errors', n_clicks=0, color="danger",
               style={'float':'right', 'display':'none'}, className="me-1"),
    dbc.Button(id='openHelper', children='Show Function', n_clicks=0, color="info", className="me-1"),
    html.Div([dash_table.DataTable(id='tableInfo')],id='page-content')
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
        id='tableInfo',
        sort_action='native',
        editable=True),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(
    Output('chartEditor','is_open'),
    Input('openEditor','n_clicks'),
    State('chartEditor','is_open'),
    prevent_initial_call=True
)

@app.callback(
    Output('errors','is_open'),
    Input('openErrors','n_clicks'),
    State('errors','is_open'),
    prevent_initial_call=True
)

@app.callback(
    Output('functions','is_open'),
    Input('openHelper','n_clicks'),
    State('functions','is_open'),
    prevent_initial_call=True
)
def openEditor(n1, isOpen):
    if n1 > 0:
        return not isOpen
    return isOpen


@app.callback(Output('contentDisplay', 'children'),
              [Input('uploadContent', 'contents')],
              [State('uploadContent', 'filename'),
               State('uploadContent', 'last_modified')],
              prevent_initial_call=True)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(
    Output('graphingOptions','children'),
    Input('selectChart','value'),
    prevent_initial_call=True,
)
def graphingOptions(chart):
    if chart:
        return getOpts(chart)

@app.callback(
    Output('page-content','children'),
    Output('errors','children'),
    Output('functionHelper','children'),
    Output('openErrors','style'),
    Input('submitEdits','n_clicks'),
    Input('tableInfo', 'data'),
    State('graphingOptions','children'),
    State('selectChart','value'),
    prevent_initial_call=True
)
def updateLayout(n1, data, opts, selectChart):
    if data and opts:
        df = pd.DataFrame.from_dict(data)
        df = df.infer_objects()
        figureDict = parseSelections(opts[1]['props']['children'],
                                             opts[2]['props']['children'])
        figureDict['chart'] = selectChart
        fig, error, func_string = makeCharts(df, figureDict)
        style = {'float': 'right', 'display': 'none'}
        if error != '':
            style = {'float':'right', 'display':'inline-block'}
        return dcc.Graph(figure=fig), error, func_string, style
    raise PreventUpdate


if __name__ == '__main__':
    app.run(debug=True)