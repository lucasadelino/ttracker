from os.path import abspath, dirname

ROOT_DIR = dirname(abspath(__file__))
DATABASE_PATH = ROOT_DIR + "/data/frags.db"

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
PRETTY_FORMAT = "%-I:%M"

######################################################################
# Terminal report (cl_report.py) preferences

# Colors to rename in the report
# By default, these are color names used by Todoist that have no direct equivalent in the terminal
# You can, however, add any renaming you want to this dictionary (as long as it matches Todoist and terminal colors)
RENAME_COLORS = {
    "sky_blue": "cyan",
}

######################################################################
# Task Selection (set_task.py) preferences

# Customize the sort preference of tasks displayed by Rofi
# Options: "project name", "project length"
SORT_BY = "project length"
