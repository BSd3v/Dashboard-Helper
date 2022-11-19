from dash import dcc, Input, Output, State, html
import plotly.express as px
from plotly.io._templates import templates
from plotly.express._core import make_figure
import plotly.graph_objects as go
import dash_mantine_components as dmc
from inspect import getmembers, isfunction, getargvalues, signature, isclass
import json
import traceback
from utils.buildCols import cols, multiCols
import os


layoutList = ["arg", "activeselection", "activeshape", "annotations", "annotationdefaults",
              "autosize", "autotypenumbers", "bargap", "bargroupgap", "barmode", "barnorm",
              "boxgap", "boxgroupgap", "boxmode", "calendar", "clickmode", "coloraxis", "colorscale",
              "colorway", "computed", "datarevision", "dragmode", "editrevision", "extendfunnelareacolors",
              "extendiciclecolors", "extendpiecolors", "extendsunburstcolors", "extendtreemapcolors", "font",
              "funnelareacolorway", "funnelgap", "funnelgroupgap", "funnelmode", "geo", "grid", "height",
              "hiddenlabels", "hiddenlabelssrc", "hidesources", "hoverdistance", "hoverlabel", "hovermode",
              "iciclecolorway", "images", "imagedefaults", "legend", "mapbox", "margin", "meta", "metasrc",
              "minreducedheight", "minreducedwidth", "modebar", "newselection", "newshape", "paper_bgcolor",
              "piecolorway", "plot_bgcolor", "polar", "scene", "selectdirection", "selectionrevision", "selections",
              "selectiondefaults", "separators", "shapes", "shapedefaults", "showlegend", "sliders",
              "sliderdefaults", "smith", "spikedistance", "sunburstcolorway", "template", "ternary",
              "title", "titlefont", "transition", "treemapcolorway", "uirevision", "uniformtext",
              "updatemenus", "updatemenudefaults", "violingap", "violingroupgap", "violinmode",
              "waterfallgap", "waterfallgroupgap", "waterfallmode", "width", "xaxis", "yaxis"]

def findFunc(selectChart):
    if 'px.' in selectChart:
        for i, y in getmembers(px, isfunction):
            if 'px.'+i == selectChart:
                return y
    else:
        for i, y in getmembers(go, isclass):
            if 'go.'+i == selectChart:
                return y

def createGo(selectChart, **kwargs) -> go.Figure:
    locals().update(kwargs)
    print(locals())
    return make_figure(args=locals(), constructor=findFunc(selectChart))

def parseSelections(opts, layout):
    args = []
    for div in opts:
        if 'id' in div['props']:
            if div['props']['id'] == 'details':
                dets = div['props']['children']
                break

    info = {}
    for inp in dets:
        if 'value' in inp['props']:
            if inp['props']['id'] == 'data_frame':
                args.append(inp['props']['id'] + '=' + inp['props']['value'] + '')
            elif inp['props']['value'] != '':
                args.append(inp['props']['id'] + '="' + str(inp['props']['value']) + '"')
                if inp['props']['value'] == 'False':
                    info[inp['props']['id']] = False
                elif inp['props']['value'] == 'True':
                    info[inp['props']['id']] = True
                else:
                    try:
                        info[inp['props']['id']] = json.loads(inp['props']['value'])
                    except:
                        info[inp['props']['id']] = inp['props']['value']

    updateLayout = {}
    for div in layout:
        if 'id' in div['props']:
            if div['props']['id'] == 'layout':
                lay = div['props']['children']
                break

    for inp in lay:
        if 'value' in inp['props']:
            if inp['props']['id'] == 'data_frame':
                args.append(inp['props']['id'].replace('layout_','') + '=' + inp['props']['value'] + '')
            elif inp['props']['value'] != '':
                args.append(inp['props']['id'].replace('layout_','') + '="' + inp['props']['value'] + '"')
                if inp['props']['value'] == 'False':
                    updateLayout[inp['props']['id'].replace('layout_', '')] = False
                elif inp['props']['value'] == 'True':
                    updateLayout[inp['props']['id'].replace('layout_', '')] = True
                else:
                    try:
                        updateLayout[inp['props']['id'].replace('layout_', '')] = json.loads(inp['props']['value'])
                    except:
                        updateLayout[inp['props']['id'].replace('layout_', '')] = inp['props']['value']

    return {'figure': info, 'layout':updateLayout}

def getOpts(selectChart, data={}):
    layout = []
    sig = signature(findFunc(selectChart))

    for param in sig.parameters.values():
        layout.append(html.Div(str(param).split('=')[0] + ':'))
        if 'data_frame' in str(param):
            layout.append(dcc.Input(id=str(param).split('=')[0],
                                placeholder=str(param).split('=')[0],
                                    value='data', disabled=True))
        else:
            if str(param).split('=')[0] in cols or str(param).split('=')[0] in multiCols:
                if str(param).split('=')[0] in multiCols:
                    layout.append(dcc.Dropdown(id=str(param).split('=')[0],
                                            placeholder=str(param).split('=')[0],
                                            persistence='memory', options=data.columns, multi=True))
                else:
                    layout.append(dcc.Dropdown(id=str(param).split('=')[0],
                                               placeholder=str(param).split('=')[0],
                                               persistence='memory', options=data.columns))
            elif str(param).split('=')[0] == 'template':
                layout.append(dcc.Dropdown(id=str(param).split('=')[0],
                                           placeholder=str(param).split('=')[0],
                                           persistence='memory', options=[t for t in templates]))

            else:
                layout.append(dcc.Input(id=str(param).split('=')[0],
                                    placeholder=str(param).split('=')[0],
                                        persistence='memory'))
    updateLayout = []

    for param in layoutList:
        updateLayout.append(html.Div(param + ':'))
        if param == 'template':
                updateLayout.append(dcc.Dropdown(id='layout_' + param,
                                           placeholder=param,
                                           persistence='memory', options=[t for t in templates]))
        else:
            updateLayout.append(dcc.Input(id='layout_' + param,
                                placeholder=param, persistence='memory',))
    return [dmc.AccordionItem([dcc.Link('API Reference', href=f'https://plotly.com/python-api-reference/generated/plotly.'
        f'express.{selectChart.replace("px.","")}.html#plotly.express.{selectChart.replace("px.","")}', target='_blank'),
                               html.Br(),
                              dcc.Link('Plotly Example Docs', href='https://plotly.com/python/', target='_blank'),
                               html.Br(),
                               dcc.Link('Layout References',
                                        href='https://plotly.com/python-api-reference/generated/plotly.graph_objects.Layout.html', target='_blank')
                               ]
                              ,label='Chart Info'),
        dmc.AccordionItem([html.Div(layout, style={'maxHeight':'50vh', 'overflowY':'auto'}, id='details')],
                              label='Chart Options'),
            dmc.AccordionItem([html.Div(updateLayout, style={'maxHeight': '50vh', 'overflowY': 'auto'}, id='layout')],
                              label='Layout Options')
            ]

def makeCharts(data, figureDict):
    selectChart = figureDict['chart']

    func_string = []

    func_string.append(html.Div(["""Figure function call representation:""",
                                 dmc.Prism('fig = ' +selectChart +'(' + ',\n'.join([key + '="' + str(value) +
                                                           '"' for key, value in figureDict['figure'].items()]) + ')',
                                  language='python'), html.Br()]))

    error = ''
    try:
        if 'px.' in selectChart:
            fig = findFunc(selectChart)(data_frame=data, **figureDict['figure'])
        else:
            fig = createGo(selectChart, **figureDict['figure'])
        if 'layout' in figureDict:
            fig.update_layout(figureDict['layout'])

            func_string.append(html.Div([
                """Updates the figure's layout:""",
                dmc.Prism('fig.update_layout(' + json.dumps(figureDict['layout']) + ")",
                                         language='python'), html.Br()]))
    except:
        fig = go.Figure()
        error = traceback.format_exc()

    func_string.append(html.Div(["""Use this with the makeCharts function to get the desired chart:""",
                                 dmc.Prism('fig = makeCharts(df,\n ' + json.dumps(figureDict).replace(',',',\n') + ')',
                                 language='python')]))

    return fig, error, func_string

def stripFigure(info):
    iDict = info.copy()
    for key in iDict:
        if key in ['chart','figure','layout']:
            info.pop(key, None)
    return info

def makeDCC_Graph(data, info):
    fig = makeCharts(data, info)[0]
    newInfo = stripFigure(info.copy())
    graph = dcc.Graph(figure=fig, **newInfo)
    return graph