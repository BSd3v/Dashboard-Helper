import json
from dash import (
    Dash,
    html,
    dcc,
    Input,
    Output,
    State,
    dash_table,
    ctx,
    page_container,
    MATCH,
    ALL,
)
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
from utils.jyadaScripts import scripts

px_list = getmembers(px, isfunction)
# go_list = getmembers(go, isclass)
chartOpts = ["px." + i for i, y in px_list]  # +['go.'+i for i, y in go_list]

preload = {
    "carshare": px.data.carshare(),
    "election": px.data.election(),
    "experiment": px.data.experiment(),
    "gapminder": px.data.gapminder(),
    "iris": px.data.iris(),
    "medals_wide": px.data.medals_wide(),
    "medals_long": px.data.medals_long(),
    "stocks": px.data.stocks(),
    "tips": px.data.tips(),
    "wind": px.data.wind(),
}


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    use_pages=True,  # pages_folder='',
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    external_scripts=[
        "https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"
    ],
)
app.clientside_callback(
    """
        function (n1, c) {
            if (n1 > 0) {
                $('#design-area .dash-graph').unbind()
                $('#design-area .dash-graph > div:first-of-type').empty()
                $('#design-area .dash-graph').on('mouseenter', function () {
                    localStorage.setItem('focused-graph',$(this)[0].id)
                    $('#design-area .dash-graph').removeClass('focused-graph')
                    $(this).addClass('focused-graph')
                })
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
    Output("design-area", "className"),
    Input("toggleEdit", "n_clicks"),
    State("design-area", "className"),
    prevent_intial_call=True,
)


def sidebar():
    return dbc.Nav(
        [
            dbc.NavItem(
                dbc.NavLink(i, href=dash.page_registry[i]["path"], active="exact")
            )
            for i in dash.page_registry
        ],
        pills=True,
        vertical=True,
    )


app.layout = html.Div(
    id="div-app",
    children=[
        dcc.Location(id="url"),
        dbc.Popover(
            [
                dbc.PopoverHeader("jyada"),
                dbc.PopoverBody("Hello!\nI am Just Your Automated Dashboard Assistant.\nBut you can call me Jyada!",
                                className='btn-info', id='jyadaPopoverConvo'),
            ],
            target="jyada",
            trigger="hover",
            placement='bottom',
            id='jyadaPopover'
        ),
        dbc.Popover(
            dbc.PopoverBody(['What do you want to do?',
                            dcc.Dropdown(id='scriptChoices')]),
            target='jyada',
            trigger='legacy',
            placement='left',
            id='jyadaScriptOptions'
        ),
        html.Img(id="jyada", src='/assets/tech-support.png', className='sleeping'),
        dbc.Modal(
            id="statusAlert",
            children=[html.Div(id="alert", className="alert-success")],
            is_open=False,
            centered=True,
        ),
        dcc.Store(id='scriptData', data=scripts, storage_type='memory'),
        dcc.Store(id="dataInfo", data=[], storage_type="local"),
        dcc.Store(id="figureStore", data=[], storage_type="local"),
        dbc.Button(
            id="sidebarButton",
            children=DashIconify(icon="fa-bars"),
            color="dark",
            style={"position": "absolute", "top": "0px", "margin": "0.5%"},
        ),
        dbc.Offcanvas(id="sidebar", children=sidebar()),
        html.Div(id="persistenceClear"),
        html.H2(
            [
                "Data and Chart Explorer",
                dbc.Button(
                    "Toggle Data Options",
                    id="collapseData",
                    color="warning",
                    style={"marginLeft": "2%"},
                ),
            ],
            id="header",
            style={"textAlign": "center", "width": "100%", "marginTop": "10px"},
        ),
        dbc.Collapse(
            id="dataOptions",
            children=[
                dcc.Loading(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Upload(
                                            id="uploadContent",
                                            children=html.Div(
                                                [
                                                    "Drag and Drop or ",
                                                    html.A("Select File"),
                                                ]
                                            ),
                                            style={
                                                "width": "98%",
                                                "height": "60px",
                                                "lineHeight": "60px",
                                                "borderWidth": "1px",
                                                "borderStyle": "dashed",
                                                "borderRadius": "5px",
                                                "textAlign": "center",
                                                "marginLeft": "1%",
                                                "marginRight": "1%",
                                                "marginTop": "1%",
                                                "cursor": "pointer",
                                                "backgroundColor": "white",
                                            },
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Plotly Datasets:",
                                            style={
                                                "marginLeft": "1%",
                                                "marginRight": "1%",
                                                "width": "98%",
                                                "marginBottom": "1%",
                                            },
                                        ),
                                        dmc.Select(
                                            id="preloadData",
                                            data=list(preload.keys()),
                                            style={
                                                "marginLeft": "1%",
                                                "marginRight": "1%",
                                                "width": "98%",
                                                "marginBottom": "1%",
                                            },
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Realtime Stock Info:",
                                            style={
                                                "marginLeft": "1%",
                                                "marginRight": "1%",
                                                "width": "98%",
                                                "marginBottom": "1%",
                                            },
                                        ),
                                        dcc.Input(
                                            placeholder="Ticker",
                                            id="stockQuery",
                                            style={
                                                "marginLeft": "1%",
                                                "marginRight": "1%",
                                                "width": "98%",
                                                "marginBottom": "1%",
                                            },
                                            debounce=True,
                                        ),
                                    ]
                                ),
                            ],
                            style={
                                "backgroundColor": "#c5c6d0",
                                "marginLeft": "1%",
                                "marginRight": "1%",
                            },
                            id="infoLoader",
                        ),
                        html.Div(
                            id="contentDisplay",
                            style={
                                "maxHeight": "25vh",
                                "overflowY": "auto",
                                "margin": "1%",
                                "border": "1pt solid silver",
                            },
                            children=[
                                dash_table.DataTable(
                                    id={"type": "tableInfo", "index": "design"}
                                )
                            ],
                        ),
                    ],
                    id="loadInfoSpinner",
                )
            ],
            is_open=True,
        ),
        html.Div(
            page_container, style={"margin": "1%", "height": "98%", "width": "98%"}
        ),
    ],
    style={"padding": "0px"},
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    sizeInBytes = len(content_string) * 3 / 4 - content_string.count('=')
    sizeInKb = sizeInBytes / 1000

    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    if sizeInKb/1000 > 4:
        df = df[:2999]
        max = dbc.Alert('The dataset is over 4mb, it has been capped at 3000 rows', color='danger')
    else:
        max = ''

    return (
        html.Div(
            [
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date)),
                max,
                dash_table.DataTable(
                    data=df.to_dict("records"),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    id={"type": "tableInfo", "index": "design"},
                    sort_action="native",
                    editable=True,
                )
            ],
            style={"width": "98%", "margin": "1%"},
        ),
        df,
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
    Output("design-holder", "id"),
    Input("design-holder", "id"),
    State("dataOptions", "is_open"),
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
    Output("dataOptions", "is_open"),
    Input("collapseData", "n_clicks"),
    State("dataOptions", "is_open"),
    prevent_initial_call=True,
)


@app.callback(
    Output("chartEditor", "is_open"),
    Input("openEditor", "n_clicks"),
    State("chartEditor", "is_open"),
    prevent_initial_call=True,
)
@app.callback(
    Output("chartDesignEditor", "is_open"),
    Input("openDesignEditor", "n_clicks"),
    State("chartDesignEditor", "is_open"),
    prevent_initial_call=True,
)
@app.callback(
    Output("sidebar", "is_open"),
    Input("sidebarButton", "n_clicks"),
    State("sidebar", "is_open"),
    prevent_initial_call=True,
)
@app.callback(
    Output("functions", "is_open"),
    Input("openHelper", "n_clicks"),
    State("functions", "is_open"),
    prevent_initial_call=True,
)
def openEditor(n1, isOpen):
    if n1 > 0:
        return not isOpen
    return isOpen


@app.callback(
    Output("chartDesignEditor_edit", "is_open"),
    Output({"type": "selectChart_edit", "index": "2"}, "value"),
    Input("editActive", "n_clicks"),
    State("chartDesignEditor_edit", "is_open"),
    State("focused-graph", "data"),
    State("figures", "data"),
    prevent_initial_call=True,
)
def openEditor_edit(n1, isOpen, id, figs):
    if n1 > 0:
        for f in figs:
            if f["id"] == json.loads(id):
                chart = f["chart"]
        return not isOpen, chart
    return isOpen


@app.callback(
    Output("errorsCanvas", "style"),
    Input("openErrors", "n_clicks"),
    State("errorsCanvas", "style"),
    prevent_initial_call=True,
)
def openErrors(n1, s):
    if n1 > 0:
        if s == {"display": "none"}:
            return {"display": "block"}
        return {"display": "none"}
    return dash.no_update


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
    Output("persistenceClear", "children"),
    [Input("uploadContent", "contents")],
    Input("preloadData", "value"),
    Input("stockQuery", "value"),
    Input({"index": ALL, "type": "persistenceClear"}, "n_clicks"),
)


@app.callback(
    Output("contentDisplay", "children"),
    Output({'index':ALL, 'type':"testFigure"}, "figure"),
    Output("dataInfo", "data"),
    [Input("uploadContent", "contents")],
    Input("preloadData", "value"),
    Input("stockQuery", "value"),
    Input('url', 'pathname'),
    [State("uploadContent", "filename"), State("uploadContent", "last_modified")],
    State('dataInfo','data'),State({'index':ALL, 'type':"testFigure"}, "figure"),
    prevent_initial_call=True
)
def update_output(c, pl, s, path, n, d, data, fig):
    if c is not None and c != '' and ctx.triggered_id == "uploadContent":
        children, df = parse_contents(c, n, d)
        if path == "/designer":
            return children, [go.Figure()]*len(fig), df.to_dict("records")
        else:
            return children, [go.Figure()]*len(fig), dash.no_update
    elif ctx.triggered_id == "preloadData":
        df = preload[pl]
        tbl = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            id={"type": "tableInfo", "index": "design"},
            sort_action="native",
            editable=True,
        )
        if path == "/designer":
            return [pl, tbl], [go.Figure()]*len(fig), df.to_dict("records")
        else:
            return [pl, tbl], [go.Figure()]*len(fig), dash.no_update
    elif ctx.triggered_id == "stockQuery":
        df = yf.Ticker(s).history(period="max").reset_index()
        df["Date"] = pd.to_datetime(df["Date"])
        if df.empty:
            raise PreventUpdate
        tbl = dash_table.DataTable(
            data=df.to_dict("records"),
            columns=[{"name": i, "id": i} for i in df.columns],
            id={"type": "tableInfo", "index": "design"},
            sort_action="native",
            editable=True,
        )
        if path == "/designer":
            return [s, tbl], [go.Figure()]*len(fig), df.to_dict("records")
        else:
            return [s, tbl], [go.Figure()]*len(fig), dash.no_update
    else:
        if path == "/designer":
            return [dash_table.DataTable(data=data, id={"type": "tableInfo", "index": "design"})],\
               [go.Figure()]*len(fig), dash.no_update
        else:
            return [dash_table.DataTable(id={"type": "tableInfo", "index": "design"})], \
                   [go.Figure()] * len(fig), dash.no_update

@app.callback(
    Output({"type": "graphingOptions", "index": MATCH}, "children"),
    Output({"type": "persistenceClear", "index": MATCH}, "style"),
    Output({"type": "submitEdits", "index": MATCH}, "style"),
    Input({"type": "selectChart", "index": MATCH}, "value"),
    Input({"type": "tableInfo", "index": MATCH}, "data"),
    Input({"index": MATCH, "type": "persistenceClear"}, "n_clicks"),
    prevent_initial_call=True,
)
def graphingOptions(chart, data, p):
    if chart:
        if not data:
            return (
                "Please load a dataset",
                {"visibility": "hidden"},
                {"visibility": "hidden"},
            )
        df = pd.DataFrame.from_dict(data)
        return getOpts(chart, df), {"visibility": True}, {"visibility": True}
    return "Please select an option", {"visibility": "hidden"}, {"visibility": "hidden"}


@app.callback(
    Output({"type": "graphingOptions_edit", "index": MATCH}, "children"),
    Output({"type": "persistenceClear_edit", "index": MATCH}, "style"),
    Output({"type": "submitEdits_edit", "index": MATCH}, "style"),
    Input({"type": "selectChart_edit", "index": MATCH}, "value"),
    Input("dataInfo", "data"),
    Input({"index": MATCH, "type": "persistenceClear_edit"}, "n_clicks"),
    State("focused-graph", "data"),
    State("figures", "data"),
    prevent_initial_call=True,
)
def graphingOptions_edit(chart, data, p, id, figs):
    if chart:
        if not data:
            return (
                "Please load a dataset",
                {"visibility": "hidden"},
                {"visibility": "hidden"},
            )
        df = pd.DataFrame.from_dict(data)
        try:
            if ctx.triggered_id["index"] == "2":
                return (
                    getOpts(chart, df, id, figs),
                    {"visibility": True},
                    {"visibility": True},
                )
        except:
            ...
        return getOpts(chart, df), {"visibility": True}, {"visibility": True}
    return "Please select an option", {"visibility": "hidden"}, {"visibility": "hidden"}


@app.callback(
    Output("page-content", "children"),
    Output("errorsCanvas", "children"),
    Output("functionHelper", "children"),
    Output("openErrors", "style"),
    Output({"type": "submitEdits", "index": ALL}, "children"),
    Output("openHelper", "className"),
    Input({"type": "submitEdits", "index": "design"}, "n_clicks"),
    State({"type": "tableInfo", "index": ALL}, "data"),
    State({"type": "graphingOptions", "index": "design"}, "children"),
    State({"type": "selectChart", "index": "design"}, "value"),
    prevent_initial_call=True,
)
def updateLayout(n1, data, opts, selectChart):
    btn = ["Make Changes"]
    if data and opts:
        df = pd.DataFrame.from_dict(data[0])
        df = df.infer_objects()
        figureDict = parseSelections(
            opts[0]["props"]["children"][1]["props"]["children"],
            opts[1]["props"]["children"][1]["props"]["children"],
        )
        figureDict["chart"] = selectChart
        fig, error, func_string = makeCharts(df, figureDict)
        style = {"float": "right", "display": "none"}
        if error != "":
            style = {"float": "right", "display": "inline-block", "marginRight": "1%"}
            errorPre = html.Pre(error)
        else:
            errorPre = ""
        if func_string != "":
            clFunc = "me-1"
        else:
            clFunc = "hidden"
        return (
            dcc.Graph(figure=fig, id={'index':'design', 'type':"testFigure"}),
            errorPre,
            func_string,
            style,
            btn,
            clFunc,
        )
    raise PreventUpdate


@app.callback(
    Output("design-area", "children"),
    Output("figures", "data"),
    Output({"type": "submitEdits_edit", "index": ALL}, "children"),
    Input({"type": "submitEdits_edit", "index": ALL}, "n_clicks"),
    Input("deleteTarget", "n_clicks"),
    Input("figureStore", "data"),
    State("dataInfo", "data"),
    State({"type": "graphingOptions_edit", "index": ALL}, "children"),
    State({"type": "selectChart_edit", "index": ALL}, "value"),
    State("design-area", "children"),
    State("focused-graph", "data"),
    State("figures", "data"),
)
def updateLayout(n1, d1, figs, data, opts, selectChart, children, target, figouts):
    btn = ["Make Changes"] * len(n1)
    if data:
        df = pd.DataFrame.from_dict(data)
        df = df.infer_objects()
        if ctx.triggered_id == "figureStore":
            children = [makeDCC_Graph(df, i) for i in figs]
            return children, figs, btn
        if data and opts and ctx.triggered_id != "deleteTarget":
            if len(children) == 0:
                figouts = []
            trig = ctx.triggered_id.index

            if trig == "edit":
                opts = opts[0]
                figureDict = parseSelections(
                    opts[0]["props"]["children"][1]["props"]["children"],
                    opts[1]["props"]["children"][1]["props"]["children"],
                )
                figureDict["chart"] = selectChart[0]

                used = []
                for child in children:
                    used.append(child["props"]["id"]["index"])

                y = 0
                while y < 1000:
                    if y not in used:
                        break
                    y += 1

                figureDict["id"] = {"index": y, "type": "design-charts"}

                if not "style" in figureDict:
                    figureDict["style"] = {
                        "position": "absolute",
                        "width": "40%",
                        "height": "40%",
                    }

                children.append(makeDCC_Graph(df, figureDict))
                figouts.append(figureDict)
                return children, figouts, btn
            else:
                opts = opts[1]
                figureDict = parseSelections(
                    opts[0]["props"]["children"][1]["props"]["children"],
                    opts[1]["props"]["children"][1]["props"]["children"],
                )
                figureDict["chart"] = selectChart[1]
                figureDict["id"] = json.loads(target)

                children = children.copy()

                for c in range(len(children)):
                    if children[c]["props"]["id"] == json.loads(target):
                        if "figure" in children[c]["props"]:
                            children[c]["props"]["figure"] = makeCharts(df, figureDict)[
                                0
                            ]
                        else:
                            figureDict["style"] = {
                                "position": "absolute",
                                "width": "40%",
                                "height": "40%",
                            }
                            children[c] = makeDCC_Graph(df, figureDict)
                figouts = figouts.copy()
                for f in range(len(figouts)):
                    if figouts[f]["id"] == json.loads(target):
                        figouts[f] = figureDict
                        figouts[f]["id"] = json.loads(target)

                return children, figouts, btn

        elif ctx.triggered_id == "deleteTarget":
            for c in range(len(children)):
                if children[c]["props"]["id"] == json.loads(target):
                    del children[c]
                    break
            for fig in figouts:
                if fig["id"] == json.loads(target):
                    figouts.remove(fig)

            return children, figouts, btn
    raise PreventUpdate


app.clientside_callback(
    """function dragging(d) {
        setTimeout(function () {
        $('#design-area .dash-graph').unbind()
        $('#design-area .dash-graph').on('mouseenter', function () {
            localStorage.setItem('focused-graph',$(this)[0].id)
            $('#design-area .dash-graph').removeClass('focused-graph')
            $(this).addClass('focused-graph')
        })
        $('#design-area .dash-graph > div:first-of-type').empty()
        $('#design-area.edit .dash-graph').each(function() {
            addEditButtons($(this).find('div')[0])
            dragElement($(this).find('.fa-up-down-left-right')[0])
        })}, 300)
        
        return window.dash_clientside.no_update
    }""",
    Output("design-area", "id"),
    Input("design-area", "children"),
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
    Output("focused-graph", "data"),
    Input("syncStore", "n_clicks"),
    prevent_initial_call=True,
)

app.clientside_callback(
    """
    function saveLayout(n1, n2) {
        const triggered = dash_clientside.callback_context.triggered.map(t => t.prop_id);
        if (triggered == 'deleteLayout.n_clicks') {
            if (confirm('You would like to delete your layout?')) {
                return [[], '', false]
            } else {
                return window.dash_clientside.no_update
            }
        }
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
            return [figureData, 'Saved Successfully', true]
        }
        return [JSON.parse(localStorage.getItem('figureStore')), '', false]
    }
    """,
    Output("figureStore", "data"),
    Output("alert", "children"),
    Output("statusAlert", "is_open"),
    Input("saveLayout", "n_clicks"),
    Input("deleteLayout", "n_clicks"),
    prevent_inital_call=True,
)


@app.callback(
    Output("layoutDownload", "data"),
    Input("exportLayout", "n_clicks"),
    State("figureStore", "data"),
    State("dataInfo", "data"),
    prevent_intial_call=True,
)
def exportLayout(n1, figs, data):
    if n1 > 0:
        return dcc.send_string(json.dumps(figs), "figs.json")
    raise PreventUpdate


@app.callback(
    Output("exampleUsage", "data"),
    Input("exampleUse", "n_clicks"),
    prevent_intial_call=True,
)
def exportLayout(n1):
    if n1 > 0:
        example = """
import dash
from dash import Dash, html
from utils.makeCharts import makeDCC_Graph
import json

app = Dash(__name__)

with open('figs.json') as f:
    figs = json.loads(f.read())
    
#df = your_data
    
app.layout = html.Div([makeDCC_Graph(df, i) for i in figs])

app.run(debug=True, port=1234)
        """
        return dcc.send_string(example, "example.txt")
    raise PreventUpdate


@app.callback(
    Output("header", "children"),
    Input("url", "pathname"),
    prevent_intial_call=True,
)
def hideDataOpts(path):
    if "/designer" not in path:
        return [
                "Explore the Data",
                dbc.Button(
                    "Toggle Data Options",
                    id="collapseData",
                    color="warning",
                    style={"marginLeft": "2%"},
                ),
            ]
    else:
        return [
            "Design your Dashboard",
            dbc.Button(
                "Toggle Data Options",
                id="collapseData",
                color="warning",
                style={"marginLeft": "2%"},
            ),
        ]

app.clientside_callback(
    """
    async function (n, o) {
        if ($("#jyada").hasClass('sleeping')) {
            return !o
        }
        return window.dash_clientside.no_update
    }
    """,
    Output('jyadaPopover','is_open'),
    Input('jyada','n_clicks'),
    State('jyadaScriptOptions','is_open'),
    prevent_initial_call = True
)

app.clientside_callback(
    """function (is) {
        if ($("#jyada").attr("convo")) {
            return $("#jyada").attr("convo")
        }
        return "Hello! I am Just Your Automated Dashboard Assistant. But you can call me Jyada!"
    }""",
    Output("jyadaPopoverConvo","children"),
    Input("jyadaPopover","is_open"),
    prevent_initial_call = True
)

app.clientside_callback(
    """
    function(o, p, d) {
        if (!$("#jyada").hasClass('sleeping')) {
            return ['hidden', window.dash_clientside.no_update]
        }
        return ['', Object.keys(d[p])]
    }
    """,
    Output('jyadaScriptOptions','className'),
    Output('scriptChoices','options'),
    Input('jyadaScriptOptions','is_open'),
    State('url','pathname'),
    State('scriptData','data'),
    prevent_initial_call = True
)

app.clientside_callback(
    """
    function(v, p, d) {
        if (v) {
            if (v != '') {
                playScript(d[p][v])
                return false
            }
        }
        return true
    }
    """,
    Output('jyadaScriptOptions','is_open'),
    Input('scriptChoices','value'),
    State('url','pathname'),
    State('scriptData','data'),
    prevent_initial_call = True
)


if __name__ == "__main__":
    app.run(debug=True)
