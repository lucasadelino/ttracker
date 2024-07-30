#!/usr/bin/python3
import json, sys, time
import threading
from datetime import datetime, timedelta
from polyserver import Server
from utils import DATABASE_PATH, DATETIME_FORMAT, ROOT_DIR
import subprocess
import sqlite3
from contextlib import closing

colors = {
    "normal": "#cfcfcf",
    "done": "#98c379",
    "urgent": "#e06c75",
    "disabled": "#707880",
}


class Timer:
    def set_task_info(self, task_jsonstr):
        task_info = json.loads(task_jsonstr)
        self.task_id = task_info[0]
        self.task_name = task_info[1]
        self.project_id = task_info[2]
        self.project_name = task_info[3]
        self.project_color = task_info[4]

    def __init__(self):
        self.stage = 0
        # Get task id and name
        if len(sys.argv) == 2:
            self.set_task_info(sys.argv[1])
        else:
            self.task_id = ""
            self.task_name = ""
            self.project_id = ""
            self.project_name = ""

        self.delta = 0
        self.server = Server("timer")
        self.running = False
        self.quit = False
        self.stage = "normal"
        server_thread = threading.Thread(target=self.check_server)
        server_thread.start()

    def start_timer(self):
        self.running = True
        now = datetime.now().strftime(DATETIME_FORMAT)
        self.frag_start_date, self.frag_start_time = now.split()
        self.frag_end_time = None

    def stop_timer(self):
        self.running = False
        now = datetime.now().strftime(DATETIME_FORMAT)
        self.frag_end_date, self.frag_end_time = now.split()
        self.log()

    def reset_timer(self):
        if self.running:
            self.stop_timer()
        self.delta = 0
        self.stage = "normal"
        self.print_time()

    def toggle_timer(self):
        if self.running:
            self.stop_timer()
        else:
            self.start_timer()

    def print_time(self):
        # TODO: dissociate minute counting and state toggling from this
        if self.delta == 1800 and self.stage != "urgent":
            self.stage = "done"
            subprocess.run(["notify-send", "Focus session done!", "-u", "low"])

        if self.delta == 3600:
            self.stage = "urgent"
            subprocess.run(["notify-send", "Consider taking a break..."])
            self.delta = 0

        minutes, seconds = divmod(self.delta, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        colored_time = f"%{{F{colors[self.stage]}}}{time_string}%{{F-}}"

        print(f"{self.task_name} - {colored_time}", flush=True)

    def handle_command(self, command):
        if command == "p":
            self.toggle_timer()
        elif command == "q":
            print("", flush=True)
            if self.running:
                self.stop_timer()
            self.quit = True
            exit()
        elif command == "r":
            self.reset_timer()
        elif command[:2] == '["':  # TODO: Maybe ignore if the task is the same?
            self.switch_task(command)

    def check_server(self):
        while True:
            message = self.server.listen()
            if message:
                self.handle_command(message)
            time.sleep(0.25)

    def switch_task(self, task_str):
        if self.running:
            self.stop_timer()
        self.set_task_info(task_str)
        self.start_timer()

    def main_loop(self):
        while not self.quit:
            if self.running:
                self.print_time()
                self.delta = self.delta + 1
            time.sleep(1)

    def log(self):
        # Save task to sqlite database
        with closing(sqlite3.connect(DATABASE_PATH)) as connection:
            cursor = connection.cursor()
            # Create table if it doesn't already exist
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS frags ("
                "task_id INTEGER, task_name TEXT,"
                "frag_start_date TEXT,  frag_start_time TEXT,"
                "frag_end_date TEXT, frag_end_time TEXT,"
                "project_id INTEGER, project_name TEXT, project_color TEXT)"
            )
            # Insert task into table
            cursor.execute(
                "INSERT INTO frags VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.task_id,
                    self.task_name,
                    self.frag_start_date,
                    self.frag_start_time,
                    self.frag_end_date,
                    self.frag_end_time,
                    self.project_id,
                    self.project_name,
                    self.project_color,
                ),
            )
            connection.commit()

        # Also save task to log text file, for convenience
        with open(f"{ROOT_DIR}/log.txt", "a") as file:
            file.writelines(
                (
                    f"ID: {self.task_id}\n",
                    f"Task name: {self.task_name}\n",
                    f"Start time: {self.frag_start_date} {self.frag_start_time}\n",
                    f"End time: {self.frag_end_date} {self.frag_end_time}\n",
                    f"Project ID: {self.project_id}\n",
                    f"Project name: {self.project_name}\n",
                    f"Project color: {self.project_color}\n",
                    "\n",
                )
            )


if __name__ == "__main__":
    Timer().main_loop()
