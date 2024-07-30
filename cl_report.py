from datetime import datetime, timedelta
from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from lib.utils import get_db_fragments, total_time, DATETIME_FORMAT, PRETTY_FORMAT
import argparse


def parse_day_argument(day_str: str) -> datetime:
    """Parses the string argument for the day and returns a datetime object"""
    date = None
    today_date = datetime.now().date()
    if day_str in ["t", "tod", "today"]:
        date = today_date
    elif day_str in ["y", "yest", "yesterday"]:
        date = today_date - timedelta(days=1)
    elif day_str.isdigit():
        # Replace the day with the given one
        date = today_date.replace(day=int(day_str))

    return date


def determine_duration_color(seconds):
    if seconds < 1800:
        return "gray"
    elif seconds < 2700:
        return "green"
    elif seconds < 3600:
        return "yellow"
    else:
        return "green"


def create_hour_table(hour_lines, hours):
    hour_table = Table(expand=False, box=None)

    hour_table.add_column("", justify="right")
    hour_table.add_column("")
    hour_table.add_column("")

    for key, value in hour_lines.items():
        ampm_hr = datetime.strptime(str(key), "%H").strftime("%-I")
        hour_table.add_row(ampm_hr, "".join(value), total_time(hours[key], True))

    return hour_table


def create_project_dist_table(projects, dot_row_width, total_focus_time):

    total_chars = dot_row_width**2

    # Create a table containing labels for the project durations
    proj_dist_label = Table(expand=False, box=None)
    proj_dist_label.add_column(justify="left")
    proj_dist_label.add_column(justify="right")

    for project_name, project_data in sorted(
        projects.items(), key=lambda x: x[1]["duration"], reverse=True
    ):
        proj_dist_label.add_row(
            f"[{project_data['color']}]{project_name}[/{project_data['color']}]:",
            f"{total_time(project_data['duration'], True)}"
            f" ({round(project_data['duration'] / total_focus_time * 100)}%)",
        )

    rounded_values = sorted(
        convert_to_ratio(
            [project["duration"] for project in projects.values()],
            total_focus_time,
            total_chars,
        ),
        reverse=True,
    )

    dot_str = ""
    j = 0

    # Assign rounded values to project info dictionary
    for project_name, project_data in sorted(
        projects.items(), key=lambda x: x[1]["duration"], reverse=True
    ):
        project_data["dots"] = rounded_values.pop(0)

        dots_printed = 0
        while dots_printed < project_data["dots"]:
            if j == dot_row_width:  # Reached the end of the row
                j = 0
                dot_str += "\n"
            dot_str += f"[{project_data['color']}]⬤ [/{project_data['color']}]"
            dots_printed += 1
            j += 1

    # Create a table grid, with the dot matrix on the left and the labels on the right
    proj_dist_grid = Table(expand=False, box=None)
    proj_dist_grid.add_column("", justify="right")
    proj_dist_grid.add_column("", justify="left", vertical="middle")
    proj_dist_grid.add_row(dot_str, proj_dist_label)

    return proj_dist_grid


def create_history_table(history_lines, projects):
    history_table = Table(box=box.SIMPLE)
    history_table.add_column("Start", justify="right")
    history_table.add_column("End", justify="right")
    history_table.add_column("", justify="left")
    history_table.add_column("Task", justify="left", no_wrap=True)
    history_table.add_column("Project", justify="right")

    # Loop through history_lines and add them to the history_table
    # Color each cell in the Project column with the corresponding project color
    for line in history_lines:
        history_table.add_row(
            line[0],
            line[1],
            line[2],
            line[3],
            f"[{projects[line[4]]['color']}]{line[4]}[/{projects[line[4]]['color']}]",
        )

    return history_table


def convert_to_ratio(values, totalie, desired_total):
    # Calculate the proportions and the initial converted values
    converted_values = [value / totalie * desired_total for value in values]

    # Round the values and calculate the difference from the desired total
    rounded_values = [round(value) for value in converted_values]
    difference = desired_total - sum(rounded_values)

    # Adjust the rounded values to make sure they sum up to the desired total
    for i in range(abs(difference)):
        # Find the index of the value with the largest fractional part (to minimize rounding error)
        fractional_parts = [value - int(value) for value in converted_values]
        if difference > 0:
            index = fractional_parts.index(max(fractional_parts))
        else:
            index = fractional_parts.index(min(fractional_parts))

        # Adjust the rounded value at the selected index
        rounded_values[index] += 1 if difference > 0 else -1

    return rounded_values


def iteratie_over_dict(result, lookup_day, tick_row_width, chunk_len):
    hours = {}
    projects = {}

    frags = 0
    total_focus_time = 0
    sessions = 0
    last_end_time = lookup_day.replace(year=1970)

    history_lines = []
    hour_lines = {}

    # inactive = "gray37"
    rename_colors = {
        "sky_blue": "cyan",
    }

    for i, item in enumerate(result):
        start_datetime = datetime.strptime(
            f'{item["start_date"]} {item["start_time"]}', DATETIME_FORMAT
        )
        start_pretty = start_datetime.strftime(PRETTY_FORMAT).rjust(5)

        end_datetime = datetime.strptime(
            f'{item["end_date"]} {item["end_time"]}', DATETIME_FORMAT
        )
        end_pretty = end_datetime.strftime(PRETTY_FORMAT).rjust(5)

        duration = (end_datetime - start_datetime).total_seconds()
        duration_pretty = total_time(duration, True)

        # Rename color if necessary
        this_color = item["project_color"]
        if this_color in rename_colors:
            this_color = rename_colors[this_color]

        # Save project duration and color
        projects.setdefault(item["project_name"], {"duration": 0, "color": this_color})
        projects[item["project_name"]]["duration"] += duration

        if i < len(result) - 1:
            next_start = datetime.strptime(
                f'{result[i+1]["start_date"]} {result[i+1]["start_time"]}',
                DATETIME_FORMAT,
            )
            if end_datetime == next_start:
                end_pretty = recolor_str(end_pretty, "gray")
            else:
                end_pretty = recolor_str(end_pretty, "red")
        else:
            end_pretty = recolor_str(end_pretty, "red")

        if start_datetime != last_end_time:
            sessions += 1
            start_pretty = recolor_str(start_pretty, "green")
        else:
            start_pretty = recolor_str(start_pretty, "gray")

        # Calculate the hours
        # Loop through the hours in the hour range, calculating chunks of 360 seconds for each hour
        # If the chunk is within the start and end time, add a green block, otherwise add a gray block
        last_end_time = end_datetime
        hour_range = list(range(start_datetime.hour, end_datetime.hour + 1))
        zero_start_hour = start_datetime.replace(minute=0, second=0)
        zero_end_hour = end_datetime.replace(minute=0, second=0)
        current_chunk = round(
            (start_datetime - zero_start_hour).total_seconds() / chunk_len
        )
        end_chunk = round((end_datetime - zero_end_hour).total_seconds() / chunk_len)
        for each_hour in hour_range:
            hour_lines.setdefault(
                each_hour, [recolor_str("▇", "black")] * tick_row_width
            )
            if each_hour == end_datetime.hour:  # If we reached the end hour
                for j in range(current_chunk, end_chunk):
                    hour_lines[each_hour][j] = recolor_str("▇", "dark_sea_green4")
            else:
                for j in range(current_chunk, tick_row_width):
                    hour_lines[each_hour][j] = recolor_str("▇", "dark_sea_green4")
            current_chunk = 0

        if len(hour_range) == 1:
            hours.setdefault(start_datetime.hour, 0)
            hours[start_datetime.hour] += int(duration)
        else:
            hours.setdefault(start_datetime.hour, 0)
            hours[start_datetime.hour] += abs(
                3600 - (start_datetime.minute * 60)
            )  # TODO maybe add seconds?

            hours.setdefault(end_datetime.hour, 0)
            hours[end_datetime.hour] += (
                end_datetime.minute * 60
            )  # TODO maybe add seconds?

            for each_hour in hour_range[1:-1]:
                hours.setdefault(each_hour, 0)
                hours[each_hour] += 3600

        history_lines.append(
            (
                start_pretty,
                end_pretty,
                duration_pretty,
                item["task_name"],
                f'{item["project_name"]}',
            )
        )
        frags += 1
        total_focus_time += duration

    return sessions, frags, total_focus_time, hours, projects, history_lines, hour_lines


def recolor_str(string, color):
    """Recolors a string with a given color, using Rich's syntax"""
    return f"[{color}]{string}[/{color}]"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates a report with the focus fragments for a given day."
    )
    parser.add_argument(
        "day",
        type=str,
        nargs="?",
        default="t",
        help="Specify the day. Allowed values are [t, tod, today] for today, [y, yest, yesterday] for yesterday, "
        "or a number for the day of the month. Defaults to today.",
    )
    args = parser.parse_args()

    lookup_day = parse_day_argument(args.day)
    result = get_db_fragments(lookup_day)

    if not result:
        print("No fragments found for that day.")
        exit()

    # Calculate widget widths based on console width
    console = Console()
    # Length of each line of ticks in characters
    if console.width <= 76:
        tick_row_width = 20
        dot_row_width = 6
    else:
        tick_row_width = 36
        dot_row_width = 10
    # Length of each chunk in seconds
    chunk_len = 3600 / tick_row_width

    sessions, frags, total_focus_time, hours, projects, history_lines, hour_lines = (
        iteratie_over_dict(result, lookup_day, tick_row_width, chunk_len)
    )

    # Create the panels that will contain the data
    session_panel = Panel(Align.center(f"{sessions}"), title="Sessions")
    frag_panel = Panel(Align.center(f"{frags}"), title="Fragments")
    time_panel = Panel(
        Align.center(total_time(total_focus_time, True)), title="Focus Time"
    )

    # Create the tables
    hour_table = create_hour_table(hour_lines, hours)
    proj_dist_grid = create_project_dist_table(
        projects,
        dot_row_width,
        total_focus_time,
    )
    history_table = create_history_table(history_lines, projects)

    # Create the layout
    layout = Layout(
        size=5
        + (history_table.row_count + 6)
        + max((hour_table.row_count + 4), (dot_row_width + 4))
    )

    layout.split_column(
        Layout(
            Panel(
                Align.center(
                    Group(
                        Columns((session_panel, frag_panel, time_panel), padding=(0, 5))
                    ),
                    vertical="middle",
                ),
                title="Totals",
                box=box.DOUBLE_EDGE,
            ),
            size=5,
            name="upper",
        ),
        Layout(
            Panel(Align.center(history_table, vertical="middle"), title="History"),
            size=(history_table.row_count + 6),
            name="middle",
        ),
        Layout(
            name="bottom",
        ),
    )

    layout["bottom"].split_row(
        Layout(
            Panel(Align.center(hour_table, vertical="middle"), title="By Hour"),
            name="bottom_left",
        ),
        Layout(
            Panel(Align.center(proj_dist_grid, vertical="middle"), title="By Project"),
            name="bottom_right",
        ),
    )

    console.size = (console.width, (layout.size))
    console.print(layout)
