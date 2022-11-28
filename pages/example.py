import dash
import dash_mantine_components as dmc
from utils.makeCharts import makeDCC_Graph
import plotly.express as px


def layout():
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
    return [
        makeDCC_Graph(
            df,
            {
                "figure": {
                    "x": "country",
                    "y": "lifeExp",
                    "color": "continent",
                    "size": "pop",
                    "animation_frame": "year",
                    "template": "presentation",
                },
                "layout": {},
                "chart": "px.scatter",
                "id": "testing",
                "style": {
                    "overflow": "auto",
                    "height": "85%",
                    "width": "80%",
                    "border": "1px solid black",
                    "position": "absolute",
                },
            },
        ),
        dmc.Prism(example, language="python", style={"float": "right", "width": "18%"}),
    ]


dash.register_page("Example", path="/example1", layout=layout)
