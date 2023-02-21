import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import psutil
import sqlite3
from datetime import datetime, timedelta
from multiprocessing import Process


WAIT_CURRENT_CPU = 5

con = sqlite3.connect('pythonDB.db')
c = con.cursor()


def round_to_secs(dt: datetime):
    """Округляет время до целых секунд"""
    extra_sec = round(dt.microsecond / 10 ** 6)
    return dt.replace(microsecond=0) + timedelta(seconds=extra_sec)


def create_table():
    """Создает необходимые таблицы в базе данных"""
    c.execute(
        'CREATE TABLE IF NOT EXISTS CurrentCpu (timecpu TEXT, valuecpu REAL)')


def data_current_entry():
    """Записывает данные о текущей загрузке процессора в БД"""
    while True:
        now = datetime.now()
        timecpu = round_to_secs(now)
        valuecpu = psutil.cpu_percent(interval=WAIT_CURRENT_CPU)
        c.execute("INSERT INTO CurrentCpu (timecpu, valuecpu) VALUES(?, ?)",
                  (timecpu, valuecpu))
        con.commit()


def graph_build():
    """Строит графики загрузки процессора"""
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    df1 = pd.read_sql(
        (f"SELECT * FROM CurrentCpu WHERE timecpu > '{one_hour_ago}'"), con)
    df2 = pd.read_sql(
        (f"SELECT strftime('%Y-%m-%d %H:%M:00', timecpu) as timeavg, ROUND(AVG(valuecpu), 2) as valueavg FROM CurrentCpu GROUP BY timeavg"), con)
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
    create_table()
    Process(target=data_current_entry).start()
    graph_build()
