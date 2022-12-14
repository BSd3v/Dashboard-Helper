import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import plotly.express as px
import plotly.graph_objects as go
from inspect import getmembers, isfunction
from utils.jyadaScripts import addScripts

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

offCanvStyle = {"borderRadius": "15px"}


def layout():
    return [
        dbc.Offcanvas(
            [
                "Select the chart type and options below",
                dcc.Dropdown(
                    id={"type": "selectChart", "index": "design"}, options=chartOpts
                ),
                dbc.Button(
                    id={"index": "design", "type": "persistenceClear"},
                    children="Clear All Values",
                    className="m-1",
                    color="info",
                    style={"visibility": "hidden"},
                ),
                dmc.Accordion(
                    id={"type": "graphingOptions", "index": "design"},
                    value="chartOptions",
                ),
                dcc.Loading(
                    dbc.Button(
                        "Make Changes",
                        id={"type": "submitEdits", "index": "design"},
                        className="m-3",
                        style={"visibility": "hidden"},
                    ),
                    id="buttonLoading",
                ),
            ],
            id="chartEditor",
            style=offCanvStyle,
        ),
        dbc.Offcanvas(
            id="functions", children=[html.Div(id="functionHelper")], style=offCanvStyle
        ),
        dbc.Button(
            id="openEditor", children="Edit Chart Details", n_clicks=0, className="me-1"
        ),
        dbc.Button(
            id="openErrors",
            children="Toggle Errors",
            n_clicks=0,
            color="danger",
            style={"float": "right", "display": "none"},
            className="me-1",
        ),
        dbc.Button(
            id="openHelper",
            children="Show Function",
            n_clicks=0,
            color="info",
            className="hidden",
        ),
        html.Div(id="errorsCanvas", children=[]),
        html.Div([dcc.Graph(id="testFigure")], id="page-content"),
    ]


dash.register_page("Explore the Data", path="/", layout=layout)

addScripts("Explore the Data",{
    "explore":[
                {'target':'dataOptions', 'convo':'this is where you can choose all sorts of '
                                                'options for uploading your data for creation'},
               {'target':'uploadContent', 'convo':'here you can drag or choose a file to upload'},
               {'target':'preloadData','convo':'here you can choose from plotly data sets'},
               {'target':'stockQuery', 'convo':'this is where you can plug in a ticker to pull data from yfinance'},
               {'target':'contentDisplay', 'convo':'once you choose a data source, the info will be displayed here'},
                {'target':'collapseData', 'convo':'you can collapse the data to make the design area larger'},
                {'target':'_pages_content', 'convo':'this is where you can test out different charts'},
               {'target':'openEditor', 'convo':'here we can make adjustments to the chart options'},
    ],
    "create chart":[
        {'target':'preloadData', 'convo':'first thing, we need to make sure we have some data,'
                                         ' let me know when you are ready to continue'},
        {'target':'toggleEdit', 'convo':'click this button if you are not already in edit mode'},
        {'target':'openEditor', 'convo':'this will open an editor to create all the available '
                                              'charts using your info', 'action':'click'},
        {'target':'chartEditor .dash-dropdown', 'convo':'select a chart type from the options,'
                                                                        ' click me to continue'},
        {'target':'chartEditor .mantine-Accordion-item:nth-child(1)',
         'convo':'here we can see all the available arguments from your selected charts'},
        {'target':'chartEditor .mantine-Accordion-item:nth-child(2)',
         'convo':'this will show you all the options for the figure layout'},
        {'target':'chartEditor .mantine-Accordion-item:nth-child(3)',
         'convo':'here is where you can see different info about the chart like '
                 'APIs for the chart, examples and layout info'},
        {'target':'_pages_content', 'convo':'when you are ready click make changes and your chart will populate here'},
        {'target':'openHelper', 'convo':'clicking here will demonstrate similar functions to what was used to create the chart'},
        {'target':'_pages_content', 'convo':'if there are errors with what you have provided, '
                                            'errors will appear here for troubleshooting. Happy exploring!'},

    ]
})
