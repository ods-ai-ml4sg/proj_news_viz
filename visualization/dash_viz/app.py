# -*- coding: utf-8 -*-
# from pathlib import PurePosixPath, Path
import collections
import json
from textwrap import dedent as d

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objs as go
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from plotly import tools
from utils import *

# TODO: Add top words


data_path = "./data"
container = load_data(data_path)
# source -> rubrics -> topics
# source is defined by directory name
# rubrics are defined by filenames in dir
# topics are defined by columns' names
k = list(container.keys())[0]  # FE: 'ria'
kk = list(container[k].keys())[0]  # FE 'sport'
# container = {'ria': {'topic_0: [1, 2, 3, 4], ...}, ...}

top_words = load_top_words(container)

# here is page template ==========================
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

left_panel = html.Div(
    style={"width": "200px", "float": "left"},
    children=[
        html.Div(
            [
                dcc.Markdown(
                    d(
                        """
                    **Источник**
                """
                    )
                ),
                dcc.Dropdown(
                    id="source",
                    options=[{"label": s, "value": s} for s in container.keys()],
                    value=list(container.keys())[0],
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(
                    d(
                        """
                    **Тип графика**
                """
                    )
                ),
                dcc.Dropdown(
                    id="type_chart",
                    options=[
                        {"label": "Ridge plot", "value": "ridge"},
                        {"label": "Bump chart", "value": "bump"},
                    ],
                    value="ridge",
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(
                    d(
                        """
                    **Рубрики**
                """
                    )
                ),
                dcc.Dropdown(
                    id="heading",
                    value=list(container[k].keys())[0],
                    options=[{"label": s, "value": s} for s in container[k].keys()],
                ),
            ]
        ),
        html.Div(
            [
                dcc.Markdown(
                    d(
                        """
                    **Темы**
                """
                    )
                ),
                dcc.Dropdown(
                    id="topics",
                    multi=True,
                    value=["topic_0", "topic_1"],
                    options=[{"label": s, "value": s} for s in container[k][kk][1]],
                ),
            ]
        ),
    ],
    className="three columns",
)

fig_div = html.Div(
    style={"margin-left": "200px"},
    children=[dcc.Graph(id="graph", figure=go.Figure())],
    className="nine columns",
)

app.layout = html.Div(
    children=[
        html.H1(children="Visualization"),
        html.Div(children=[left_panel, fig_div]),
        html.Div([html.H2(children="Топ слов по темам"), html.Div(id="top_words",)]),
    ],
    className="twelve columns",
)
# end of page template =======================

# All callbacks ===========
@app.callback(Output("heading", "options"), [Input("source", "value")])
def update_heading(source):
    options = [
        {"label": heading, "value": heading} for heading in container[source].keys()
    ]
    return options


@app.callback(
    Output("topics", "options"), [Input("source", "value"), Input("heading", "value")]
)
def update_topics(source, heading):

    topics = container[source][heading][1]
    options = [{"label": topic, "value": topic} for topic in topics]
    return options


@app.callback(
    Output("top_words", "children"),
    [Input("source", "value"), Input("heading", "value"), Input("topics", "value")],
)
def update_top_words(source, heading, topics):
    result = []
    for topic in topics:
        div = html.Div(
            [
                html.H5(children=f"{heading} {topic}"),
                html.Div(children=", ".join(top_words[heading][topic])),
            ],
            className="one columns",
        )
        result.append(div)
    return result


@app.callback(
    Output("graph", "figure"),
    [
        Input("source", "value"),
        Input("type_chart", "value"),
        Input("heading", "value"),
        Input("topics", "value"),
    ],
)
def update_graph(source, type_chart, rubric, selected_topics):  # add_data_names
    df, topics = container[source][rubric]

    if type_chart == "ridge":
        figure = ridge_plot(df, selected_topics)
    elif type_chart == "bump":
        figure = bump_chart(df, selected_topics)

    figure["layout"]["xaxis"].update()  # (range=initial_range)

    return figure


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)
