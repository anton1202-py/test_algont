import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sqlite3
from datetime import datetime, timedelta


def graph_build():
    """Строит графики загрузки процессора"""
    con = sqlite3.connect("pythonDB4.db")
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    df1 = pd.read_sql(
        (f"SELECT * FROM CurrentCpu WHERE timecpu > '{one_hour_ago}'"), con)
    df2 = pd.read_sql(
        (f"SELECT * FROM AverageCpu WHERE timeavg > '{one_hour_ago}'"), con)
    app = dash.Dash(__name__)

    app.layout = html.Div(
        children=[
            html.H1(children='CPU Analytics',),
            html.H2(
                children='Анализ загрузки процессора',
            ),
            dcc.Graph(
                id='current-cpu',
                figure={
                    'data': [
                        {
                            'x': df1['timecpu'],
                            'y': df1['valuecpu'],
                            'type': 'bar',
                        },
                    ],
                    'layout': {'title': 'График текущей загрузки процессора'},
                },
            ),
            dcc.Graph(
                id='average-cpu',
                figure={
                    'data': [
                        {
                            'x': df2['timeavg'],
                            'y': df2['valueavg'],
                            'type': 'bar',
                        },
                    ],
                    'layout': {'title': 'График средней загрузки процессора'},
                },
            ),
        ]
    )
    return app.run_server(debug=True, host='127.0.0.1')


if __name__ == "__main__":
    graph_build()
