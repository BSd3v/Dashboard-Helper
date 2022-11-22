import json

from dash import Dash, html, dcc, Input, Output, State, dash_table, ctx, page_container, MATCH, ALL
import dash
from dash.exceptions import PreventUpdate
from inspect import getmembers, isfunction, getargvalues, signature, isclass
import dash_bootstrap_components as dbc
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



app = Dash(__name__, suppress_callback_exceptions=True, use_pages=True, #pages_folder='',
           external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            external_scripts=["https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"]
           )
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

def sidebar():
    return dbc.Nav(
        [dbc.NavItem(dbc.NavLink(i, href=dash.page_registry[i]['path'], active='exact')) for i in dash.page_registry],
        pills=True,
        vertical=True
    )

app.layout = html.Div(id='div-app',children=[
    dcc.Location(id='url'),
    dcc.Store(id='dataInfo',data=[], storage_type='local'),
    dcc.Store(id='figureStore', data=[], storage_type='local'),
    dbc.Button(id='sidebarButton', children=DashIconify(icon="fa-bars"),
               color="dark", style={'position':'absolute', 'top':'0px', 'margin': '0.5%'}),
    dbc.Offcanvas(id='sidebar', children=sidebar()),
    html.Div(id='persistenceClear'),
    html.H2(['Data and Chart Explorer',
             dbc.Button('Toggle Data Options', id='collapseData',
                                                  color="warning", style={'marginLeft':'2%'})],
            style={'textAlign':'center', 'width':'100%', 'marginTop':'10px'}),
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
                   'marginLeft':'1%',
                    'marginRight':'1%',
                    'marginTop':'1%',
                   'cursor':'pointer',
                   'backgroundColor':'white'
               },
               )]),dbc.Col([
    dmc.Select(label='Plotly Datasets:',id='preloadData', data=list(preload.keys()),
               style={'marginLeft':'1%', 'marginRight':'1%', 'width':'98%',
                      'marginBottom':'1%',})]),dbc.Col([
    dmc.TextInput(label='Realtime Stock Info', placeholder='Ticker', id='stockQuery',
                  style={'marginLeft':'1%', 'marginRight':'1%', 'width':'98%',
                      'marginBottom':'1%'}),
        ])], style={'backgroundColor':'#c5c6d0', 'marginLeft':'1%',
                    'marginRight':'1%'}),
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
        id={'type':'tableInfo', 'index':1},
        sort_action='native',
        editable=True,)

        # html.Hr(),  # horizontal line
        #
        # # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # }),
    ], style={'width':'98%', 'margin':'1%'}
), df

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
    Output('chartDesignEditor_edit','is_open'),
    Output({'type':'selectChart_edit','index':'2'},'value'),
    Input('editActive','n_clicks'),
    State('chartDesignEditor_edit','is_open'),
    State('focused-graph', 'data'),
    State('figures', 'data'),
    prevent_initial_call=True
)
def openEditor_edit(n1, isOpen, id, figs):
    if n1 > 0:
        for f in figs:
            if f['id'] == json.loads(id):
                chart = f['chart']
        return not isOpen, chart
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
                Output('dataInfo','data'),
              [Input('uploadContent', 'contents')],
              Input('preloadData', 'value'),
              Input('stockQuery','value'),
              [State('uploadContent', 'filename'),
               State('uploadContent', 'last_modified')],
              prevent_initial_call=True)
def update_output(c, pl, s, n, d):
    if c is not None and ctx.triggered_id == 'uploadContent':
        children, df = parse_contents(c, n, d)
        return children, go.Figure(), df.to_dict('records')
    elif ctx.triggered_id == 'preloadData':
        df = preload[pl]
        tbl = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            id={'type':'tableInfo', 'index':1},
            sort_action='native',
            editable=True, )
        return [pl, tbl], go.Figure(), df.to_dict('records')
    elif ctx.triggered_id == 'stockQuery':
        df = yf.Ticker(s).history(period='max').reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        if df.empty:
            raise PreventUpdate
        tbl = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            id={'type':'tableInfo', 'index':1},
            sort_action='native',
            editable=True, )
        return [s, tbl], go.Figure(), df.to_dict('records')


@app.callback(
    Output({'type':'graphingOptions','index':MATCH},'children'),
    Input({'type':'selectChart','index':MATCH},'value'),
    Input('dataInfo', 'data'),
    prevent_initial_call=True,
)

def graphingOptions(chart, data):
    if chart:
        df = pd.DataFrame.from_dict(data)
        return getOpts(chart, df)

@app.callback(
    Output({'type':'graphingOptions_edit','index':MATCH},'children'),
    Input({'type':'selectChart_edit','index':MATCH},'value'),
    Input('dataInfo', 'data'),
    State('focused-graph', 'data'),
    State('figures', 'data'),
    prevent_initial_call=True,
)

def graphingOptions_edit(chart, data, id, figs):
    if chart:
        df = pd.DataFrame.from_dict(data)
        if ctx.triggered_id['index'] == '2':
            return getOpts(chart, df, id, figs)
        return getOpts(chart, df)

@app.callback(
    Output('page-content','children'),
    Output('errors','children'),
    Output('functionHelper','children'),
    Output('openErrors','style'),
    Output('openErrors','n_clicks'),
    Input({'type':'submitEdits', 'index':'design'},'n_clicks'),
    State({'type':'tableInfo', 'index':ALL}, 'data'),
    State({'type':'graphingOptions', 'index':'design'},'children'),
    State({'type':'selectChart', 'index':'design'},'value'),
    State('openErrors','n_clicks'),
    prevent_initial_call=True
)
def updateLayout(n1, data, opts, selectChart, n2):
    if data and opts:
        df = pd.DataFrame.from_dict(data[0])
        df = df.infer_objects()
        figureDict = parseSelections(opts[1]['props']['children'],
                                             opts[2]['props']['children'])
        figureDict['chart'] = selectChart
        fig, error, func_string = makeCharts(df, figureDict)
        style = {'float': 'right', 'display': 'none'}
        if error != '':
            style = {'float':'right', 'display':'inline-block', 'marginRight':'1%'}
        else:
            n2 = 0
        return dcc.Graph(figure=fig, id='testFigure'), error, func_string, style, n2
    raise PreventUpdate

@app.callback(
    Output('design-area','children'),
    Output('figures', 'data'),
    Input({'type': 'submitEdits_edit', 'index': ALL}, 'n_clicks'),
    Input('deleteTarget', 'n_clicks'),
    Input('figureStore', 'data'),
    State('dataInfo', 'data'),
    State({'type': 'graphingOptions_edit', 'index': ALL}, 'children'),
    State({'type': 'selectChart_edit', 'index': ALL}, 'value'),
    State('design-area','children'),
    State('focused-graph','data'),
    State('figures', 'data'),
)
def updateLayout(n1, d1, figs, data, opts, selectChart, children, target, figouts):
    if data:
        df = pd.DataFrame.from_dict(data)
        df = df.infer_objects()
        if ctx.triggered_id == 'figureStore' and figs:
            children = [makeDCC_Graph(df, i) for i in figs]
            return children, figs
        if data and opts and ctx.triggered_id != 'deleteTarget':
            if len(children) == 0:
                figouts = []
            trig = ctx.triggered_id.index

            if trig == 'edit':
                opts = opts[0]
                figureDict = parseSelections(opts[1]['props']['children'],
                                             opts[2]['props']['children'])
                figureDict['chart'] = selectChart[0]

                used = []
                for child in children:
                    used.append(child['props']['id']['index'])

                y = 0
                while y < 1000:
                    if y not in used:
                        break
                    y += 1


                figureDict['id'] = {'index':y, 'type':'design-charts'}

                if not 'style' in figureDict:
                    figureDict['style'] = {'position':'absolute', 'width':'40%', 'height': '40%'}

                children.append(makeDCC_Graph(df, figureDict))
                figouts.append(figureDict)
                return children, figouts
            else:
                opts = opts[1]
                figureDict = parseSelections(opts[1]['props']['children'],
                                             opts[2]['props']['children'])
                figureDict['chart'] = selectChart[1]

                for child in children:
                    if child['props']['id'] == json.loads(target):
                        child['props']['figure'] = makeCharts(df, figureDict)[0]
                figouts = figouts.copy()
                for f in range(len(figouts)):
                    if figouts[f]['id'] == json.loads(target):
                        figouts[f] = figureDict
                        figouts[f]['id'] = json.loads(target)

                return children, figouts

        elif ctx.triggered_id == 'deleteTarget':
            for c in range(len(children)):
                if children[c]['props']['id'] == json.loads(target):
                    del children[c]
                    break
            for fig in figouts:
                if fig['id'] == json.loads(target):
                    figouts.remove(fig)

            return children, figouts
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

app.clientside_callback(
    """
        function (n1) {
            if (n1 > 0) {
                return localStorage.getItem('focused-graph')
            }
            return ''
        }
    """,
    Output('focused-graph','data'),
    Input('syncStore','n_clicks'),
    prevent_initial_call=True
)

app.clientside_callback(
    """
    function saveLayout(n1) {
        if (n1 > 0) {
            figures = JSON.parse(localStorage.getItem('figures'))
            figureData = []
            children = $("#design-area").children()
            ref = $("#design-area")[0].getBoundingClientRect()
            for (y=0; y < figures.length; y++) {
                for (x=0; x < children.length; x++) {
                    if (JSON.stringify(figures[y].id) == children[x].id) {
                        styling = children[x].style.cssText.split('; ')
                        style = {}
                        for (z=0; z<styling.length;z++) {
                            if (styling[z].split(': ')[1].split(';')[0].includes('px')) {
                                if (['height', 'top'].includes(styling[z].split(':')[0])) {
                                    adj = (parseFloat(styling[z].split(': ')[1].split(';')[0]) / ref.height)*100 + '%'
                                } else {
                                    adj = (parseFloat(styling[z].split(': ')[1].split(';')[0]) / ref.width)*100 + '%'
                                }
                                style[styling[z].split(':')[0]] = adj
                            } else {
                                style[styling[z].split(':')[0]] = styling[z].split(': ')[1].split(';')[0]
                            }
                        }
                        figures[y]['style'] = style
                        break
                    }
                }
                figureData.push(figures[y])
            }
            return figureData
        }
        return JSON.parse(localStorage.getItem('figureStore'))
    }
    """,
    Output('figureStore','data'),
    Input('saveLayout','n_clicks'),
    prevent_inital_call=True
)

if __name__ == '__main__':
    app.run(debug=True)
