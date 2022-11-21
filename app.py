from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx, page_container, MATCH
import dash
from dash.exceptions import PreventUpdate
from inspect import getmembers, isfunction, getargvalues, signature, isclass
import dash_bootstrap_components as dbc
from dash_mantine_components import Accordion as acc
import dash_mantine_components as dmc
from utils.makeCharts import makeCharts, getOpts, parseSelections, makeDCC_Graph
import yfinance as yf
from dash_iconify import DashIconify

import datetime, base64, io, pandas as pd

import plotly.express as px
import plotly.graph_objects as go

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

offCanvStyle= {'border-radius':'15px'}

app = Dash(__name__, suppress_callback_exceptions=True, use_pages=True, pages_folder='',
           external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            external_scripts=["https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"]
           )


def home():
    return [
        dbc.Offcanvas(['Select the chart type and options below',
                       dcc.Dropdown(id='selectChart', options=chartOpts),
                       dbc.Button('Make Changes', id='submitEdits'),
                       acc(id='graphingOptions'),
                       ], id='chartEditor', style=offCanvStyle),
        dbc.Offcanvas(id='functions', children=[html.Div(id='functionHelper')], style=offCanvStyle),
        dbc.Button(id='openEditor', children='Edit Chart Details', n_clicks=0, className="me-1",
                   style={'margin-left': '1%'}),
        dbc.Button(id='openErrors', children='Toggle Errors', n_clicks=0, color="danger",
                   style={'float': 'right', 'display': 'none', 'margin-right': '2%'}, className="me-1"),
        dbc.Button(id='openHelper', children='Show Function', n_clicks=0, color="info", className="me-1"),
        html.Div(id='errorsCanvas', children=[html.Pre(id='errors')],
                 style={'display': 'none'}),
        html.Div([dash_table.DataTable(id='tableInfo'),dcc.Graph(id='testFigure')
                  ], id='page-content')]

dash.register_page('Data and Chart Explorer', path='/', layout=home)

def exmaple1():
    example = """
df = px.data.gapminder()

return makeDCC_Graph(df,
    {"figure": 
        {"x": "country",
        "y": "lifeExp",
        "color": "continent",
        "size": "pop",
        "animation_frame": "year",
        "template":"presentation"},
    "layout": {},
    "chart": "px.scatter",
    'id':'testing',
    'style':{'overflow':'auto',
            'height':'85%',
            'width':'80%',
            'border':'1px solid black', 
            'position':'absolute'
            }
    })"""
    df = px.data.gapminder()
    return [makeDCC_Graph(df,
                          {"figure": {"x": "country",
                                      "y": "lifeExp",
                                      "color": "continent",
                                      "size": "pop",
                                      "animation_frame": "year",
                                      "template":"presentation"},
                           "layout": {},
                           "chart": "px.scatter", 'id': 'testing',
                           'style': {'overflow': 'auto',
                                     'height': '85%', 'width': '80%',
                                     'border': '1px solid black', 'position': 'absolute'}}),
            dmc.Prism(example,
                      language='python', style={'float': 'right', 'width': '18%'})]

dash.register_page('Example', path='/emaple1', layout=exmaple1)

def designArea():
    return html.Div([
                     html.Div(id='design-area', children=[], style={'background-color':'#c5c6d0',
                                                       'position':'absolute', 'height':'100%',
                                                       'width':'100%'}),
                    dcc.Graph(id='testFigure', style={'display':'none'}),
                     dbc.Offcanvas(['Select the chart type and options below',
                                    dcc.Dropdown(id='selectDesignChart', options=chartOpts),
                                    dbc.Button('Make Changes', id='submitDesignEdits'),
                                    acc(id='graphingDesignOptions'),
                                    ], id='chartDesignEditor', style=offCanvStyle),
                    html.Div([
                    dbc.Button('Toggle Edit Mode', id='toggleEdit', color="warning", className="me-1", n_clicks=0),
                    dbc.Button(id='openDesignEditor', children='Add Chart', n_clicks=0, className="me-1"),
                    dbc.Button(id='saveLayout', children='Save Layout', n_clicks=0, className="me-1", color='success'),
                        ], style={'z-index':'1', 'position':'absolute', 'width':'100%'})
                     ], id='design-holder')

app.clientside_callback(
    """
        function (n1, c) {
            if (n1 > 0) {
                $('#design-area .dash-graph').unbind()
                $('#design-area .dash-graph > div:first-of-type').empty()
                if (c == 'edit') {
                    $("#design-holder").removeClass('edit')
                    return ''
                }
                $("#design-holder").addClass('edit')
                $('#design-area .dash-graph').each(function() {
                    addEditButtons($(this).find('div')[0])
                    dragElement($(this).find('.fa-up-down-left-right')[0])
                })
                return 'edit'
            }
            return window.dash_clientside.no_update
        }
    """,
    Output('design-area','className'),
    Input('toggleEdit','n_clicks'),
    State('design-area','className'),
    prevent_intial_call=True
)
def toggleEdit(n1, c):
    if n1 > 0:
        if c:
            if c == 'edit':
                return '', ''
        return 'edit','edit'
    return dash.no_update, dash.no_update

dash.register_page('Designer', path='/design_area', layout=designArea)

def sidebar():
    return dbc.Nav(
        [dbc.NavItem(dbc.NavLink(i, href=dash.page_registry[i]['path'], active='exact')) for i in dash.page_registry],
        pills=True,
        vertical=True
    )

app.layout = html.Div(id='div-app',children=[
    dcc.Location(id='url'),
    dbc.Button(id='sidebarButton', children=DashIconify(icon="fa-bars"),
               color="dark", style={'position':'absolute', 'top':'0px', 'margin': '0.5%'}),
    dbc.Offcanvas(id='sidebar', children=sidebar()),
    html.Div(id='persistenceClear'),
    html.H2(['Data and Chart Explorer',
             dbc.Button('Toggle Data Options', id='collapseData',
                                                  color="warning", style={'margin-left':'2%'})],
            style={'text-align':'center', 'width':'100%', 'margin-top':'10px'}),
    dbc.Collapse(id='dataOptions',children=[
    dbc.Row([dbc.Col([
    dcc.Upload(id='uploadContent',
               children=html.Div([
                   'Drag and Drop or ',
                   html.A('Select File')
               ]),
               style={
                   'width': '98%',
                   'height': '60px',
                   'lineHeight': '60px',
                   'borderWidth': '1px',
                   'borderStyle': 'dashed',
                   'borderRadius': '5px',
                   'textAlign': 'center',
                   'margin-left':'1%',
                    'margin-right':'1%',
                    'margin-top':'1%',
                   'cursor':'pointer',
                   'background-color':'white'
               },
               )]),dbc.Col([
    dmc.Select(label='Plotly Datasets:',id='preloadData', data=list(preload.keys()),
               style={'margin-left':'1%', 'margin-right':'1%', 'width':'98%',
                      'margin-bottom':'1%',})]),dbc.Col([
    dmc.TextInput(label='Realtime Stock Info', placeholder='Ticker', id='stockQuery',
                  style={'margin-left':'1%', 'margin-right':'1%', 'width':'98%',
                      'margin-bottom':'1%'}),
        ])], style={'background-color':'#c5c6d0', 'margin-left':'1%',
                    'margin-right':'1%'}),
    html.Div(id='contentDisplay', style={'maxHeight': '25vh', 'overflowY': 'auto',
                                                 'margin': '1%',
                                                 'border': '1pt solid silver'},
                     )], is_open=True),
    html.Div(page_container, style={'margin':'1%', 'height':'98%', 'width':'98%'})
], style={'padding':'0px'})

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
        editable=True,),

        # html.Hr(),  # horizontal line
        #
        # # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # }),
    ], style={'width':'98%', 'margin':'1%'}
)

app.clientside_callback(
    """
        function (n1, isOpen) {
            if (!isOpen) {
                $("#design-holder").addClass('expanded')
            }
            return window.dash_clientside.no_update
        }
    """,
    Output('design-holder','id'),
    Input('design-holder','id'),
    State('dataOptions','is_open')
)


app.clientside_callback(
    """
        function (n1, isOpen) {
            if (n1 > 0) {
                $("#design-holder").toggleClass('expanded')
                return !isOpen
            }
            return true
        }
    """,
    Output('dataOptions','is_open'),
    Input('collapseData','n_clicks'),
    State('dataOptions','is_open'),
    prevent_initial_call=True
)


@app.callback(
    Output('chartEditor','is_open'),
    Input('openEditor','n_clicks'),
    State('chartEditor','is_open'),
    prevent_initial_call=True
)

@app.callback(
    Output('chartDesignEditor','is_open'),
    Input('openDesignEditor','n_clicks'),
    State('chartDesignEditor','is_open'),
    prevent_initial_call=True
)

@app.callback(
    Output('sidebar','is_open'),
    Input('sidebarButton','n_clicks'),
    State('sidebar','is_open'),
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


@app.callback(
    Output('errorsCanvas','style'),
    Input('openErrors','n_clicks'),
    State('errorsCanvas','style'),
    prevent_initial_call=True
)
def openErrors(n1, s):
    if n1 > 0:
        if s == {'display':'none'}:
            return {'display': 'block'}
        return {'display':'none'}
    return {'display':'none'}

app.clientside_callback(
    """function () {
        const keys = Object.keys(localStorage)
        const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);
        if (typeof oldTrig !== 'undefined') {
            if (oldTrig == triggered) {
                return ''
            }
        }
        oldTrig = triggered
        for (let key of keys) {
            if (String(key).includes('_dash_persistence') && !String(key).includes('template')) {
                localStorage.removeItem(key)
            }
        }
        return ''
    }""",
    Output('persistenceClear','children'),
    [Input('uploadContent', 'contents')],
    Input('preloadData', 'value'),
    Input('stockQuery','value')
)


@app.callback(Output('contentDisplay', 'children'),
              Output('testFigure','figure'),
              [Input('uploadContent', 'contents')],
              Input('preloadData', 'value'),
              Input('stockQuery','value'),
              [State('uploadContent', 'filename'),
               State('uploadContent', 'last_modified')],
              prevent_initial_call=True)
def update_output(c, pl, s, n, d):
    if c is not None and ctx.triggered_id == 'uploadContent':
        children = parse_contents(c, n, d)
        return children, go.Figure()
    elif ctx.triggered_id == 'preloadData':
        df = preload[pl]
        tbl = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            id='tableInfo',
            sort_action='native',
            editable=True, )
        return [pl, tbl], go.Figure()
    elif ctx.triggered_id == 'stockQuery':
        df = yf.Ticker(s).history(period='max').reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        if df.empty:
            raise PreventUpdate
        tbl = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            id='tableInfo',
            sort_action='native',
            editable=True, )
        return [s, tbl], go.Figure()


@app.callback(
    Output('graphingOptions','children'),
    Input('selectChart','value'),
    Input('tableInfo', 'data'),
    prevent_initial_call=True,
)

@app.callback(
    Output('graphingDesignOptions','children'),
    Input('selectDesignChart','value'),
    Input('tableInfo', 'data'),
    prevent_initial_call=True,
)
def graphingOptions(chart, data):
    if chart:
        df = pd.DataFrame.from_dict(data)
        return getOpts(chart, df)

@app.callback(
    Output('page-content','children'),
    Output('errors','children'),
    Output('functionHelper','children'),
    Output('openErrors','style'),
    Output('openErrors','n_clicks'),
    Input('submitEdits','n_clicks'),
    State('tableInfo', 'data'),
    State('graphingOptions','children'),
    State('selectChart','value'),
    State('openErrors','n_clicks'),
    prevent_initial_call=True
)
def updateLayout(n1, data, opts, selectChart, n2):
    if data and opts:
        df = pd.DataFrame.from_dict(data)
        df = df.infer_objects()
        figureDict = parseSelections(opts[1]['props']['children'],
                                             opts[2]['props']['children'])
        figureDict['chart'] = selectChart
        fig, error, func_string = makeCharts(df, figureDict)
        style = {'float': 'right', 'display': 'none'}
        if error != '':
            style = {'float':'right', 'display':'inline-block', 'margin-right':'1%'}
        else:
            n2 = 0
        return dcc.Graph(figure=fig, id='testFigure'), error, func_string, style, n2
    raise PreventUpdate

@app.callback(
    Output('design-area','children'),
    Input('submitDesignEdits','n_clicks'),
    State('tableInfo', 'data'),
    State('graphingDesignOptions','children'),
    State('selectDesignChart','value'),
    State('design-area','children'),
    prevent_initial_call=True
)
def updateLayout(n1, data, opts, selectChart, children):
    if data and opts:
        df = pd.DataFrame.from_dict(data)
        df = df.infer_objects()
        figureDict = parseSelections(opts[1]['props']['children'],
                                             opts[2]['props']['children'])
        figureDict['chart'] = selectChart

        figureDict['id'] = {'index':len(children), 'type':'design-charts'}

        if not 'style' in figureDict:
            figureDict['style'] = {'position':'absolute', 'width':'40%', 'height': '40%'}

        children.append(makeDCC_Graph(data, figureDict))
        return children
    raise PreventUpdate


app.clientside_callback(
    """function dragging(d) {
        setTimeout(function () {
        $('#design-area .dash-graph').unbind()
        $('#design-area .dash-graph > div:first-of-type').empty()
        $('#design-area.edit .dash-graph').each(function() {
            addEditButtons($(this).find('div')[0])
            dragElement($(this).find('.fa-up-down-left-right')[0])
        })}, 300)
        return window.dash_clientside.no_update
    }""",
    Output('design-area', 'id'),
    Input('design-area','children')
)

if __name__ == '__main__':
    app.run(debug=True)
