from datetime import datetime, timedelta
from multiprocessing import Process
import psutil
import sqlite3
import time as tm


WAIT_CURRENT_CPU = 5
WAIT_AVERAGE_CPU = 60

conn = sqlite3.connect('pythonDB4.db')
c = conn.cursor()


def round_to_secs(dt: datetime):
    """Округляет время до целых секунд"""
    extra_sec = round(dt.microsecond / 10 ** 6)
    return dt.replace(microsecond=0) + timedelta(seconds=extra_sec)


def create_table():
    """Создает необходимые таблицы в базе данных"""
    c.execute(
        'CREATE TABLE IF NOT EXISTS CurrentCpu (timecpu INTEGER, valuecpu REAL)')
    c.execute(
        'CREATE TABLE IF NOT EXISTS AverageCpu (timeavg INTEGER, valueavg REAL)')


def data_current_entry():
    """Записывает данные о текущей загрузке процессора в БД"""
    while True:
        now = datetime.now()
        timecpu = round_to_secs(now)
        valuecpu = psutil.cpu_percent(interval=WAIT_CURRENT_CPU)
        c.execute("INSERT INTO CurrentCpu (timecpu, valuecpu) VALUES(?, ?)",
                  (timecpu, valuecpu))
        conn.commit()


def data_average_entry():
    """Записывает данные о средней загрузке процессора в БД"""
    while True:
        now = datetime.now()
        timeavg = round_to_secs(now)
        valueavg = [
            x / psutil.cpu_count() * 100 for x in psutil.getloadavg()][0]
        c.execute("INSERT INTO AverageCpu (timeavg, valueavg) VALUES(?, ?)",
                  (timeavg, valueavg))
        conn.commit()
        tm.sleep(WAIT_AVERAGE_CPU)


if __name__ == '__main__':
    create_table()
    Process(target=data_average_entry).start()
    Process(target=data_current_entry).start()
