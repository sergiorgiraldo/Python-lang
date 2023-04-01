from subprocess import run
import os
from datetime import datetime

def notify(title: str, text: str) -> int:
    #save in file
    filename = os.path.expanduser("~/tmp/timelapse.log.md")
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")

    with open(filename, "a") as f:
        f.write(timestamp + text + "\n")