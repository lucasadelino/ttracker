import subprocess
from rofi import Rofi
import os
from os.path import abspath, dirname
from lib.utils import ROOT_DIR

rofi = Rofi(rofi_args=["-theme", f"{ROOT_DIR}/timer_ctrl.rasi", "-no-sort"])
options = ["play/pause", "reset", "quit"]
actual_options = ["p", "r", "q"]

i, key = rofi.select("TTracker Cmd", options)

if key == -1:  # Esc key
    exit()

chosen_option = actual_options[i]

# Transmit the chosen option to the polybar timer module
subprocess.Popen(["python3", f"{ROOT_DIR}/lib/polyclient.py", "timer", chosen_option])

# If the user chose to reset or quit a fragment, also transmit the chosen option to the polybar session module
if chosen_option in ["r", "q"]:
    subprocess.Popen(
        ["python3", f"{ROOT_DIR}/lib/polyclient.py", "session", chosen_option]
    )
