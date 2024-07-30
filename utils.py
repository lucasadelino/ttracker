import sqlite3

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"


def get_db_fragments(day):
    """Reads the fragments database and returns the fragments for the given day"""

    # Read the frags db searching for today's date
    connection = sqlite3.connect("frags.db")
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
