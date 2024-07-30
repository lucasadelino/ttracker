import sqlite3
from os.path import abspath, dirname

ROOT_DIR = dirname(dirname(abspath(__file__)))
DATABASE_PATH = ROOT_DIR + "/data/frags.db"

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
PRETTY_FORMAT = "%-I:%M"


def get_db_fragments(day):
    """Reads the fragments database and returns the fragments for the given day"""

    # Read the frags db searching for today's date
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Read row from frags.db where the date is today
    # Save the result as a dictionary and append it to the result list
    query = """SELECT * FROM frags WHERE start_date = ?"""
    result = cursor.execute(
        query,
        (day.strftime(DATE_FORMAT),),
    ).fetchall()
    connection.close()

    return result


def total_time(seconds: int, letters=False) -> str:
    """Convert seconds to a string of hours and minutes"""
    result = ""
    minutes_spent = seconds / 60
    if minutes_spent >= 60:
        hours_spent, minutes_spent = divmod(minutes_spent, 60)
        result += f'{int(hours_spent)}{"h" if letters else ":"}'
        if minutes_spent > 0:
            result += f"{int(minutes_spent):02d}"
    else:
        result += f'{int(minutes_spent)}{"m" if letters else ""}'

    return result
