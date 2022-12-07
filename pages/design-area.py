import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from pages.home import offCanvStyle, chartOpts
import dash_mantine_components as dmc
from utils.jyadaScripts import addScripts


def layout():
    return html.Div(
        [
            html.Div(
                id="design-area",
                children=[],
                style={
                    "backgroundColor": "#c5c6d0",
                    "position": "absolute",
                    "height": "100%",
                    "width": "100%",
                },
            ),
            dcc.Graph(id="testFigure", style={"display": "none"}),
            dcc.Store(id="focused-graph", storage_type="local"),
            dcc.Store(id="figures", storage_type="local", data=[]),
            dbc.Offcanvas(
                [
                    "Select the chart type and options below",
                    dcc.Dropdown(
                        id={"index": "edit", "type": "selectChart_edit"},
                        options=chartOpts,
                    ),
                    dbc.Button(
                        id={"index": "edit", "type": "persistenceClear_edit"},
                        children="Clear All Values",
                        className="m-3",
                        color="info",
                        style={"visibility": "hidden"},
                    ),
                    dmc.Accordion(
                        id={"index": "edit", "type": "graphingOptions_edit"},
                        value="chartOptions",
                    ),
                    dcc.Loading(
                        [
                            dbc.Button(
                                "Make Changes",
                                id={"index": "edit", "type": "submitEdits_edit"},
                                className="m-3",
                                style={"visibility": "hidden"},
                            ),
                        ],
                        id="buttonLoading_edit",
                    ),
                ],
                id="chartDesignEditor",
                style=offCanvStyle,
            ),
            dbc.Offcanvas(
                [
                    "Select the chart type and options below",
                    dcc.Dropdown(
                        id={"index": "2", "type": "selectChart_edit"}, options=chartOpts
                    ),
                    dbc.Button(
                        id={"index": "2", "type": "persistenceClear_edit"},
                        children="Clear All Values",
                        className="m-3",
                        color="info",
                        style={"visibility": "hidden"},
                    ),
                    dmc.Accordion(
                        id={"index": "2", "type": "graphingOptions_edit"},
                        value="chartOptions",
                    ),
                    dcc.Loading(
                        [
                            dbc.Button(
                                "Make Changes",
                                id={"index": "2", "type": "submitEdits_edit"},
                                className="m-3",
                                style={"visibility": "hidden"},
                            )
                        ],
                        id="buttonLoading_edit",
                    ),
                ],
                id="chartDesignEditor_edit",
                style=offCanvStyle,
            ),
            html.Div(
                [
                    dbc.Button(
                        "Toggle Edit Mode",
                        id="toggleEdit",
                        color="warning",
                        className="me-1",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        id="openDesignEditor",
                        children="Add Chart",
                        n_clicks=0,
                        className="me-1",
                    ),
                    dbc.Button(
                        id="saveLayout",
                        children="Save Layout",
                        n_clicks=0,
                        className="me-1",
                        color="success",
                    ),
                    dbc.Button(
                        id="exportLayout",
                        children="Export Layout",
                        n_clicks=0,
                        className="me-1",
                        color="info",
                    ),
                    dcc.Download(id="layoutDownload"),
                    dbc.Button(
                        id="exampleUse",
                        children="Example Usage",
                        n_clicks=0,
                        className="me-1",
                        color="info",
                    ),
                    dbc.Button(
                        id="deleteLayout",
                        children="Delete Layout",
                        n_clicks=0,
                        className="me-1",
                        color="danger",
                    ),
                    dcc.Download(id="exampleUsage"),
                ],
                style={"zIndex": "1", "position": "absolute", "width": "100%"},
            ),
            dbc.Button(id="editActive", style={"display": "none"}),
            dbc.Button(id="syncStore", style={"display": "none"}),
            dbc.Button(id="deleteTarget", style={"display": "none"}),
        ],
        id="design-holder",
    )


dash.register_page("Design your Dashboard", path="/designer", layout=layout)

addScripts("Design your Dashboard",{
    "explore":[
                {'target':'dataOptions', 'convo':'this is where you can choose all sorts of '
                                                'options for uploading your data for creation'},
               {'target':'uploadContent', 'convo':'here you can drag or choose a file to upload'},
               {'target':'preloadData','convo':'here you can choose from plotly data sets'},
               {'target':'stockQuery', 'convo':'this is where you can plug in a ticker to pull data from yfinance'},
               {'target':'contentDisplay', 'convo':'once you choose a data source, the info will be displayed here'},
                {'target':'collapseData', 'convo':'you can collapse the data to make the design area larger'},
                {'target':'design-holder', 'convo':'this is where you can design your layout'},
               {'target':'toggleEdit', 'convo':'here you can toggle edit mode to make changes'},
               {'target':'exportLayout', 'convo':'this will let you export your saved layout as a json '
                                                 'file of figures'},
               {'target':'exampleUse', 'convo':'if you download this text file, it will show you an example way'
                                               ' that you can use the figure json and your chosen dataframe in your'
                                               ' own projects'}],
    "create layout":[
        {'target':'design-holder', 'convo':'here is where we are going to design our layout'},
        {'target':'preloadData', 'convo':'first thing, we need to make sure we have some data,'
                                         ' let me know when you are ready to continue'},
        {'target':'toggleEdit', 'convo':'click this button if you are not already in edit mode'},
        {'target':'openDesignEditor', 'convo':'this will open an editor to create all the available '
                                              'charts using your info', 'action':'click'},
        {'target':'chartDesignEditor .dash-dropdown', 'convo':'select a chart type from the options,'
                                                                        ' click me to continue'},
        {'target':'chartDesignEditor .mantine-Accordion-item',
         'convo':'here we can see all the available arguments from your selected chart'},
        {'target':'chartDesignEditor .mantine-Accordion-item:nth-child(2)',
         'convo':'this will show you all the options for the figure layout'},
        {'target':'chartDesignEditor .mantine-Accordion-item:nth-child(3)',
         'convo':'here is where you can see different info about the chart like '
                 'APIs for the chart, examples and layout info'},
        {'target':'design-area', 'convo':'when you are ready click make changes and your chart will populate here'},
        {'target':'design-area .dash-graph', 'convo':'there are a couple things to note here. '
                                         'You can resize the chart in the lower right hand corner. You can also '
                                         'move the chart by clicking and dragging on the move icon. '
                                         'You can also edit and delete with the other icons.'},
        {'target':'saveLayout', 'convo':'once you get a layout you like, click Save Layout to save your work'},
        {'target':'deleteLayout', 'convo':'if you want to start from scratch, click Delete Layout'},
        {'target':'design-area', 'convo':'one other thing of note, all automatically generated charts will have '
                                         'pattern matching ids assigned for use in your applications. Happy designing!'}
    ]
})
