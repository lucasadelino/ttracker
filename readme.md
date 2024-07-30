![ttracker logo](ttracker_logo.svg?raw=true "ttracker logo")

A simple time tracker for Todoist.

# Features
- Track how much time you spend in your Todoist tasks
- Free-flow time tracking, so your timer fits your focus sessions, and not the opposite.
- Generate beautiful terminal reports, including statistics on time spent focused for each hour and for each project.

![ttracker report example](cl_log.png?raw=true "ttracker report example")

# Requirements
- dotenv
- polybar
- rich
- rofi
- python-rofi
- TodoistAPI for Python

For displaying session and focus time icons in Polybar, you need the [Material Design Iconic font](https://zavoloklom.github.io/material-design-iconic-font/). 

# Motivation
This project was born out of a desire for tracking the time I spent on my Todoist tasks. I love Todoist for its simplicity, ease of use, and for offering a WearOS app and a pretty comprehensive API. However, Todoist lacks any built-in time tracking. There are great external tools for doing this, like [Toggl](https://toggl.com/), [Ellie](https://ellieplanner.com/), and [Sunsama](https://www.sunsama.com/), but they are all much much more complex than what I needed. If I'm using an extra app on top of Todoist, I would like that app to be as minimal as possible. 

This is where ttracker comes in. It's built on the assumption that most of your organizational heavy lifting is done on Todoist. Interacting with ttracker mostly amounts to running a couple of Python scripts, which I have bound to hotkeys in my system. You interact with these scripts via Rofi, which provides even more ease of use and customizability. Your focus data is saved in a .db file, so you can run your own queries if you wish. If you don't, ttracker also comes with a command-line tool to generate reports in your terminal.   

To sum it up, this project is likely to be useful to you if you:
- Use Todoist to manage most or all of your daily tasks  
- Already use Polybar and Rofi
- Are used to having terminals open, and would like to view your focus reports there

# Usage
## Controlling the timer
- Create a `.env` file in the ttracker root folder, containing your todoist API token.
- Use `set_task.py` to choose a Todoist task and start a timer. 
  - `set_task.py` pulls all your Todoist tasks that are due today, launches a Rofi menu so that you can choose task, and starts a timer with your selected task.
  - The timer is displayed as a Polybar module. The timer will change color to green once thirty minutes have elapsed, and to red once an hour has elapsed.
- Use `timer_ctl.py` to pause, reset, or end the timer. 
- A record of all your focus sessions is saved in a .db file in the ttracker root folder.

## Generating reports
- Use `cl_report.py` to generate a report of your focus time for a given day.
  - The syntax for this command is `cl_report.py DAY`. If `DAY` is not specified, it defaults to today's date. You can also pass `y`, `yest`, or `yesterday` to generate a report for yesterday, or a number `N` to generate a report for that day of the month (e.g. `cl_report.py 3` or `cl_report.py 23`).

# Roadmap
- Add support for more user preferences to customize task selection and report behavior
- Add more planning features, such as support for estimating time and comparing estimated with actual time spent on each task.
