from dash import dcc, Input, Output, State, html
import plotly.express as px
from plotly.io._templates import templates
from plotly.express._core import make_figure
import plotly.graph_objects as go
import dash_mantine_components as dmc
from inspect import getmembers, isfunction, getargvalues, signature, isclass
import json
import traceback
from utils.buildCols import getColumns


layoutList = [
    "arg",
    "activeselection",
    "activeshape",
    "annotations",
    "annotationdefaults",
    "autosize",
    "autotypenumbers",
    "bargap",
    "bargroupgap",
    "barmode",
    "barnorm",
    "boxgap",
    "boxgroupgap",
    "boxmode",
    "calendar",
    "clickmode",
    "coloraxis",
    "colorscale",
    "colorway",
    "computed",
    "datarevision",
    "dragmode",
    "editrevision",
    "extendfunnelareacolors",
    "extendiciclecolors",
    "extendpiecolors",
    "extendsunburstcolors",
    "extendtreemapcolors",
    "font",
    "funnelareacolorway",
    "funnelgap",
    "funnelgroupgap",
    "funnelmode",
    "geo",
    "grid",
    "height",
    "hiddenlabels",
    "hiddenlabelssrc",
    "hidesources",
    "hoverdistance",
    "hoverlabel",
    "hovermode",
    "iciclecolorway",
    "images",
    "imagedefaults",
    "legend",
    "mapbox",
    "margin",
    "meta",
    "metasrc",
    "minreducedheight",
    "minreducedwidth",
    "modebar",
    "newselection",
    "newshape",
    "paper_bgcolor",
    "piecolorway",
    "plot_bgcolor",
    "polar",
    "scene",
    "selectdirection",
    "selectionrevision",
    "selections",
    "selectiondefaults",
    "separators",
    "shapes",
    "shapedefaults",
    "showlegend",
    "sliders",
    "sliderdefaults",
    "smith",
    "spikedistance",
    "sunburstcolorway",
    "template",
    "ternary",
    "title",
    "titlefont",
    "transition",
    "treemapcolorway",
    "uirevision",
    "uniformtext",
    "updatemenus",
    "updatemenudefaults",
    "violingap",
    "violingroupgap",
    "violinmode",
    "waterfallgap",
    "waterfallgroupgap",
    "waterfallmode",
    "width",
    "xaxis",
    "yaxis",
]


def findFunc(selectChart):
    if "px." in selectChart:
        for i, y in getmembers(px, isfunction):
            if "px." + i == selectChart:
                return y
    else:
        for i, y in getmembers(go, isclass):
            if "go." + i == selectChart:
                return y


def createGo(selectChart, **kwargs) -> go.Figure:
    locals().update(kwargs)
    print(locals())
    return make_figure(args=locals(), constructor=findFunc(selectChart))


def parseSelections(opts, layout):
    args = []
    dets = opts["props"]["children"]

    info = {}
    for inp in dets:
        if "value" in inp["props"]:
            if inp["props"]["id"] == "data_frame":
                args.append(inp["props"]["id"] + "=" + inp["props"]["value"] + "")
            elif inp["props"]["value"] != "" and inp["props"]["value"]:
                args.append(
                    inp["props"]["id"] + '="' + str(inp["props"]["value"]) + '"'
                )
                if inp["props"]["value"] and inp["props"]["value"] != '':
                    if isinstance(inp["props"]["value"], str):
                        if inp["props"]["value"].lower() == "false":
                            info[inp["props"]["id"].replace("layout_", "")] = False
                        elif inp["props"]["value"].lower() == "true":
                            info[inp["props"]["id"].replace("layout_", "")] = True
                        else:
                            try:
                                info[
                                    inp["props"]["id"].replace("layout_", "")
                                ] = json.loads(inp["props"]["value"])
                            except:
                                info[inp["props"]["id"].replace("layout_", "")] = inp[
                                    "props"
                                ]["value"]
                    else:
                        info[
                            inp["props"]["id"].replace("layout_", "")
                        ] = inp["props"]["value"]

    updateLayout = {}
    lay = layout["props"]["children"]

    for inp in lay:
        if "value" in inp["props"]:
            if inp["props"]["id"] == "data_frame":
                args.append(
                    inp["props"]["id"].replace("layout_", "")
                    + "="
                    + str(inp["props"]["value"])
                    + ""
                )
            elif inp["props"]["value"] != "":
                args.append(
                    inp["props"]["id"].replace("layout_", "")
                    + '="'
                    + str(inp["props"]["value"])
                    + '"'
                )
                if inp["props"]["value"] and inp["props"]["value"] != '':
                    if isinstance(inp["props"]["value"], str):
                        if inp["props"]["value"].lower() == "false":
                            updateLayout[inp["props"]["id"].replace("layout_", "")] = False
                        elif inp["props"]["value"].lower() == "true":
                            updateLayout[inp["props"]["id"].replace("layout_", "")] = True
                        else:
                            try:
                                updateLayout[
                                    inp["props"]["id"].replace("layout_", "")
                                ] = json.loads(inp["props"]["value"])
                            except:
                                updateLayout[inp["props"]["id"].replace("layout_", "")] = inp[
                                    "props"
                                ]["value"]
                    else:
                        updateLayout[
                            inp["props"]["id"].replace("layout_", "")
                        ] = inp["props"]["value"]
    return {"figure": info, "layout": updateLayout}


def getOpts(selectChart, data={}, id=None, figs=None):
    layout = []
    sig = signature(findFunc(selectChart))

    cols, multiCols= getColumns(selectChart)

    if id:
        for f in figs:
            if f["id"] == json.loads(id):
                figureData = f["figure"]
                layData = f["layout"]
    else:
        figureData = {}
        layData = {}

    if 'y_multi' in figureData:
        if figureData['y_multi']:
            y_multi = True
            y_multi_value = figureData['y_multi']
        else:
            y_multi = False
            y_multi_value = []
    else:
        y_multi = False
        y_multi_value = []

    for param in sig.parameters.values():
        layout.append(html.Div(str(param).split("=")[0] + ":", className="dbc"))
        if "data_frame" in str(param):
            layout.append(
                dcc.Input(
                    id=str(param).split("=")[0],
                    placeholder=str(param).split("=")[0],
                    value="data",
                    disabled=True,
                )
            )
        else:
            if str(param).split("=")[0] in figureData:
                val = figureData[str(param).split("=")[0]]
            else:
                val = ""
            if (
                str(param).split("=")[0] in cols
                or str(param).split("=")[0] in multiCols
            ):
                if str(param).split("=")[0] in multiCols:
                    layout.append(
                        dcc.Dropdown(
                            id=str(param).split("=")[0],
                            value=val,
                            placeholder=str(param).split("=")[0],
                            options=data.columns,
                            multi=y_multi,
                        )
                    )
                    if str(param).split("=")[0] == 'y':
                        layout.append(dcc.Checklist(options=[{'label':'multi column y?','value':True}],
                                                    value=y_multi_value, id='y_multi'))
                else:
                    layout.append(
                        dcc.Dropdown(
                            id=str(param).split("=")[0],
                            value=val,
                            placeholder=str(param).split("=")[0],
                            options=data.columns,
                        )
                    )
            elif str(param).split("=")[0] == "template":
                layout.append(
                    dcc.Dropdown(
                        id=str(param).split("=")[0],
                        value=val,
                        placeholder=str(param).split("=")[0],
                        options=[t for t in templates],
                    )
                )

            else:
                if not isinstance(val, str):
                    val = json.dumps(val)
                layout.append(
                    dcc.Input(
                        id=str(param).split("=")[0],
                        value=val,
                        placeholder=str(param).split("=")[0],
                    )
                )
    updateLayout = []

    for param in layoutList:
        updateLayout.append(html.Div(param + ":"))
        if param in layData:
            val = layData[str(param).split("=")[0]]
        else:
            val = ""
        if param == "template":
            updateLayout.append(
                dcc.Dropdown(
                    id="layout_" + param,
                    placeholder=param,
                    value=val,
                    options=[t for t in templates],
                )
            )
        else:
            if not isinstance(val, str):
                val = json.dumps(val)
            updateLayout.append(
                dcc.Input(
                    id="layout_" + param,
                    value=val,
                    placeholder=param,
                )
            )
    return [
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Chart Options"),
                dmc.AccordionPanel(
                    html.Div(
                        layout,
                        style={"maxHeight": "50vh", "overflowY": "auto"},
                        id="details",
                    )
                ),
            ],
            value="chartOptions",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Layout Options"),
                dmc.AccordionPanel(
                    html.Div(
                        updateLayout,
                        style={"maxHeight": "50vh", "overflowY": "auto"},
                        id="layout",
                    )
                ),
            ],
            value="layoutOptions",
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl("Chart Info"),
                dmc.AccordionPanel(
                    [
                        dcc.Link(
                            "API Reference",
                            href=f"https://plotly.com/python-api-reference/generated/plotly."
                            f'express.{selectChart.replace("px.", "")}.html#plotly.express.{selectChart.replace("px.", "")}',
                            target="_blank",
                        ),
                        html.Br(),
                        dcc.Link(
                            "Plotly Example Docs",
                            href="https://plotly.com/python/",
                            target="_blank",
                        ),
                        html.Br(),
                        dcc.Link(
                            "Layout References",
                            href="https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html",
                            target="_blank",
                        ),
                    ]
                ),
            ],
            value="chartInfo",
        ),
    ]


def makeCharts(data, figureDict):
    selectChart = figureDict["chart"]

    func_string = []

    func_string.append(
        html.Div(
            [
                """Figure function call representation:""",
                dmc.Prism(
                    "fig = "
                    + selectChart
                    + "("
                    + ",\n".join(
                        [
                            key + '="' + str(value) + '"'
                            for key, value in figureDict["figure"].items()
                        ]
                    )
                    + ")",
                    language="python",
                ),
                html.Br(),
            ]
        )
    )

    error = ""
    try:
        figureInfo = figureDict["figure"].copy()
        figureInfo.pop('y_multi', None)
        if "px." in selectChart:
            fig = findFunc(selectChart)(data_frame=data, **figureInfo)
        else:
            fig = createGo(selectChart, **figureInfo)
        if "layout" in figureDict:
            fig.update_layout(figureDict["layout"])

            func_string.append(
                html.Div(
                    [
                        """Updates the figure's layout:""",
                        dmc.Prism(
                            "fig.update_layout("
                            + json.dumps(figureDict["layout"])
                            + ")",
                            language="python",
                        ),
                        html.Br(),
                    ]
                )
            )
    except:
        fig = go.Figure()
        error = traceback.format_exc()

    func_string.append(
        html.Div(
            [
                """Use this with the makeCharts function to get the desired chart:""",
                dmc.Prism(
                    "fig = makeCharts(df,\n "
                    + json.dumps(figureDict).replace(",", ",\n")
                    + ")",
                    language="python",
                ),
            ]
        )
    )

    return fig, error, func_string


def stripFigure(info):
    iDict = info.copy()
    for key in iDict:
        if key in ["chart", "figure", "layout"]:
            info.pop(key, None)
    return info


def makeDCC_Graph(data, info):
    fig, error, func_string = makeCharts(data, info)
    newInfo = stripFigure(info.copy())
    graph = dcc.Graph(figure=fig, **newInfo)
    if error != "":
        print(error)
        if "style" in newInfo:
            newInfo["style"]["display"] = "flex"
            newInfo["style"]["justifyContent"] = "center"
            newInfo["style"]["alignItems"] = "center"
        graph = html.Div(
            [
                html.Div(),
                "uhoh, something didnt work quite right -- check your python console",
            ],
            className="dash-graph",
            **newInfo,
        )
    return graph
