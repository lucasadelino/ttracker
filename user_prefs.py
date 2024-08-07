from os.path import abspath, dirname

ROOT_DIR = dirname(abspath(__file__))
DATABASE_PATH = ROOT_DIR + "/data/frags.db"

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
PRETTY_FORMAT = "%-I:%M"

# set_task preferences

# Customize the sort preference of tasks displayed by Rofi
# Options: "project name", "project length"
SORT_BY = "project length"
