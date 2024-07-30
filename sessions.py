#!/usr/bin/python3
from datetime import datetime
from utils import DATETIME_FORMAT
import os
from os.path import abspath, dirname
from cl_report import total_time
from utils import get_db_fragments
from polyserver import Server
import time

os.chdir(dirname(abspath(__file__)))

sep_color = "#707880"
sep = f"%{{F{sep_color}}}|%{{F-}}"
session_icon = ""
time_icon = ""
today = datetime.now().date()


def calculate_sessions():
    """ "Reads the results from the fragment database and returns the number of sessions and total time spent focusing today"""

    result = get_db_fragments(today)
    sessions = 0
    total_seconds = 0
    last_end_time = today.replace(year=1970)

    for item in result:
        start_datetime = datetime.strptime(
            f'{item["start_date"]} {item["start_time"]}', DATETIME_FORMAT
        )
        end_datetime = datetime.strptime(
            f'{item["end_date"]} {item["end_time"]}', DATETIME_FORMAT
        )
        total_seconds += (end_datetime - start_datetime).total_seconds()
        if start_datetime != last_end_time:
            sessions += 1
        last_end_time = end_datetime

    total_str = total_time(total_seconds, True)

    return sessions, total_str


# When this script first runs, calculate the sessions and total time spent focusing today
first_iteration = True
# After that, listen on the 'session' UNIX socket for 'reset' or 'quit' commands by the user:
server = Server("session")
while True:
    if first_iteration:
        message = True
    else:
        message = server.listen()

    if message:
        sessions, total_str = calculate_sessions()
        print(f"{session_icon} {sessions} {sep} {time_icon} {total_str}", flush=True)

    if first_iteration:
        first_iteration = False

    time.sleep(1)
