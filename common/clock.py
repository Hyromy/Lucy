import threading
import datetime
import pytz
import asyncio

from utils.SQL import SQLHelper

from .activies import draw_spliter

def _minutes():
    pass

def _hours():
    pass

def _days():
    current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
    date = current.strftime(" %d/%m/%Y ")
    draw_spliter(text = date)

    sql = SQLHelper()
    try:
        sql.build_from_cache()
    except:
        sql.load_cache(True)
        sql.build_from_cache()
    finally:
        sql.close_conection()
    del sql

async def _clock_minute():
    while True:
        current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
        s = current.second
        await asyncio.sleep(60 - s)
        _minutes()

async def _clock_hour():
    while True:
        current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
        s = current.second
        m = current.minute * 60
        await asyncio.sleep(3600 - (s + m))
        _hours()

async def _clock_day():
    while True:
        current = datetime.datetime.now(pytz.timezone("America/Mexico_City"))
        s = current.second
        m = current.minute * 60
        h = current.hour * 3600
        await asyncio.sleep(86400 - (s + m + h))
        _days()

async def _clock_main():
    await asyncio.gather(
        _clock_minute(),
        _clock_hour(),
        _clock_day()
    )

def start_clock():
    threading.Thread(
        target = lambda:asyncio.run(_clock_main()),
        name = "ClockThread"
    ).start()