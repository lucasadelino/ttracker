from math import e
from numpy import full
from todoist_api_python.api import TodoistAPI
from datetime import datetime
from rofi import Rofi
import subprocess
import json
import os
from dotenv import load_dotenv, find_dotenv
from lib.utils import ROOT_DIR
from user_prefs import SORT_BY

os.chdir((ROOT_DIR))

# Read API key from .env file
load_dotenv(find_dotenv())
api = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))

today_date = datetime.now().strftime("%Y-%m-%d")
rofi = Rofi(rofi_args=["-theme", "set_task.rasi", "-i", "-markup-rows"])
results = []
parents = set()

id_dict = {}  # Dict with all tasks due today
other_dict = {}  # Dict with all tasks NOT due today
bottom_only = {}  # Dict with all tasks that don't have children
displayed_ids = []
displayed_contents = []
project_list = []  # Just for sorting, later

max_task_len = 0
max_project_len = 0

project_id_dict = {}

# Get all projects
print("Getting projects from API...")
try:
    projects = api.get_projects()
    for project in projects:
        project_id_dict[project.id] = {"name": project.name, "color": project.color}
        if len(project.name) > max_project_len:
            max_project_len = len(project.name)
except Exception as error:
    print("Could not get projects. Error:")
    print(error)
    exit()


print("Getting tasks from API...")
try:
    tasks = api.get_tasks()
    print("Got tasks from API!")
    for task in tasks:
        if task.parent_id:  # If the task has a parent, save it for later
            parents.add(task.parent_id)
        if task.due and task.due.date == today_date:
            id_dict[task.id] = {
                "content": task.content,
                "project_id": task.project_id,
                "section_id": task.section_id,
                "labels": task.labels,
                "parent_id": task.parent_id,
            }
        else:  # TODO: Make function to avoid repeating code
            other_dict[task.id] = {
                "content": task.content,
                "project_id": task.project_id,
                "parent_id": task.parent_id,
            }


except Exception as error:
    print("Could not get tasks. Error:")
    results = None
    print(error)
    print(str(error))
    rofi.error(str(error))
    exit()

# Find all the tasks that have parents but don't have children
# For those tasks, find the full parent path and save it as a string
print("Making task display strings...")
for task_id, task_info in id_dict.items():
    if task_id not in parents:
        parent_id = task_info["parent_id"]
        display_str = ""
        while parent_id:
            # Check first if we already have the parent task content
            try:
                display_str = id_dict[parent_id]["content"] + "/" + display_str
                parent_id = id_dict[parent_id]["parent_id"]
            # If not, get it from the API
            except KeyError:
                display_str = other_dict[parent_id]["content"] + "/" + display_str
                parent_id = other_dict[parent_id]["parent_id"]
                # parent_task = api.get_task(parent_id)
            # parent = id_dict[parent]["parent_id"]
        displayed_ids.append(task_id)
        display_str += task_info["content"]
        displayed_contents.append(display_str)

        if len(display_str) > max_task_len:
            max_task_len = len(display_str)


width = 0

print("Making project display strings...")
for i, task_id in enumerate(displayed_ids):
    task_info = id_dict[task_id]
    display_task = displayed_contents[i]
    this_project = "#" + project_id_dict[task_info["project_id"]]["name"]
    project_list.append(this_project)
    # Add pango markup to color the project name
    display_project = f'<span fgalpha="60%" style="italic">{this_project}</span>'
    print(len(display_task))
    full_str = f"{display_task.ljust(40)}{display_project.rjust(60)}"
    displayed_contents[i] = full_str

    if len(full_str) > width:
        width = len(full_str)

rofi = Rofi(
    rofi_args=[
        "-theme",
        "set_task.rasi",
        "-i",
        "-markup-rows",
        "-theme-str",
        f"window{{ width: {int(width/1.58)}ch; }}",
    ]
)

if SORT_BY:
    if SORT_BY == "project name":
        key = lambda x: x[0]
    elif SORT_BY == "project length":
        key = lambda x: len(x[0])

    assert key, "Invalid SORT_BY value"

    project_list, displayed_contents, displayed_ids = zip(
        *sorted(zip(project_list, displayed_contents, displayed_ids), key=key)
    )

i, key = rofi.select(
    "TTracker Set",
    displayed_contents,
)


if key == -1:  # Exit if user presses the esc key
    exit()

chosen_id = displayed_ids[i]

project_name = project_id_dict[id_dict[chosen_id]["project_id"]]["name"]
project_color = project_id_dict[id_dict[chosen_id]["project_id"]]["color"]
dump = json.dumps(
    (
        chosen_id,
        id_dict[chosen_id]["content"],
        id_dict[chosen_id]["project_id"],
        project_name,
        project_color,
        id_dict[chosen_id]["section_id"],
        id_dict[chosen_id]["labels"],
    )
)
subprocess.Popen(["python3", f"{ROOT_DIR}/lib/polyclient.py", "timer", dump])
