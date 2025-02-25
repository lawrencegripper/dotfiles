#!/usr/bin/env -S uv run --with PyQt5 --script

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
#     "icalevents",
#     "humanize",
#     "BlinkStick",
#     "pyusb",
#     "libusb",
# ]
# ///

from icalevents.icalevents import events, Event
import os
import subprocess
import base64
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dateutil import tz
import time
from humanize import naturaltime
from PyQt5.QtWidgets import QApplication, QMessageBox
from blinkstick import blinkstick

blinkStickClient: blinkstick.BlinkStick = blinkstick.find_first()


def get_op_value(path):
    cache_dir = "/tmp/ghcal"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, base64.urlsafe_b64encode(path.encode()).decode())

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return file.read().strip()
    else:
        value = subprocess.check_output(["/bin/bash", "-c", f"op read '{path}'"]).decode().strip()
        with open(cache_file, 'w') as file:
            file.write(value)
        os.chmod(cache_file, 0o600)
        return value

def sort_by_date(e: Event):
    if e.start is not None:
        return e.start.astimezone()
    else:
        return datetime.min.replace(tzinfo=tz.tzutc())

def fetch_ical_file(app_password, username, url):
    cache_file = "/tmp/ghcal.ics"
    if os.path.exists(cache_file):
        last_modified_time = os.path.getmtime(cache_file)
        if time.time() - last_modified_time < 300:  # 300 seconds = 5 minutes
            return

    response = requests.get(url, auth=HTTPBasicAuth(username, app_password))

    if response.status_code == 200:
        with open(cache_file, "wb") as file:
            file.write(response.content)
        os.chmod(cache_file, 0o600)
    else:
        raise Exception(f"Failed to download calendar: {response.status_code} {response.text}")

app_password = get_op_value("op://Private/ghcal-app-password/password")
username = get_op_value("op://Private/ghcal-app-password/username")

url = f"https://www.google.com/calendar/dav/{username}/events"

fetch_ical_file(app_password, username, url)

es = events(file="/tmp/calendar.ics")

es.sort(key=sort_by_date)

for event in es:
    if event.start is None:
        continue

    if event.start < datetime.now(tz=tz.tzlocal()):
        continue

    time_until_start = event.start - datetime.now(tz=tz.tzlocal())

    if time_until_start.total_seconds() > (60 * 60 * 8):
        print(f"Event more than 8 hours away")
        break

    print(f"Event: {event.summary} in {naturaltime(event.start)}")

    if time_until_start.total_seconds() < 120:
        app = QApplication([])
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Meeting Reminder")
        msg_box.setText(f"'{event.summary}' is about to start.\n\nDo you acknowledge that you might miss it?")
        font = msg_box.font()
        font.setPointSize(25)
        msg_box.setFont(font)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        result = msg_box.exec_()
        
        if time_until_start.total_seconds() < 60:
            blinkStickClient.blink(name="red", repeats=7, delay=1000)
    
    # print(f"Starts in: {days} days, {hours} hours, and {minutes} minutes")
