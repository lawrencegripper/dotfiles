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
import pickle

blinkStickClient: blinkstick.BlinkStick = blinkstick.find_first()

cache_dir = "/tmp/ghcal"
cache_all_events = f"{cache_dir}/all.ics"
cache_today_pkl = f"{cache_dir}/today.pkl"
os.makedirs(cache_dir, exist_ok=True)
os.chmod(cache_dir, 0o700)

def get_todays_events(sort_by_date):
    if os.path.exists(cache_today_pkl):
        last_modified_time = os.path.getmtime(cache_today_pkl)
        if time.time() - last_modified_time < 300:  # 300 seconds = 5 minutes
            with open(cache_today_pkl, 'rb') as file:
                es = pickle.load(file)
            es.sort(key=sort_by_date)
            return es

    start_of_today = datetime.now(tz=tz.tzlocal()).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today.replace(hour=23, minute=59, second=59)

    es = events(file=cache_all_events, start=start_of_today, end=end_of_today)
    es.sort(key=sort_by_date)
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_today_pkl, 'wb') as file:
        pickle.dump(es, file)
    return es

def get_op_value(path):
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
    cache_file = cache_all_events
    if os.path.exists(cache_file):
        last_modified_time = os.path.getmtime(cache_file)
        if time.time() - last_modified_time < 300:  # 300 seconds = 5 minutes
            return

    response = requests.get(url, auth=HTTPBasicAuth(username, app_password))

    if response.status_code == 200:
        with open(cache_file, "wb") as file:
            file.write(response.content)
        os.chmod(cache_file, 0o600)
        if os.path.exists(cache_today_pkl):
            os.remove(cache_today_pkl)  # force a re-read of today's events from the new file
    else:
        raise Exception(f"Failed to download calendar: {response.status_code} {response.text}")
    
def format_color(color: str, text: str):
        return "%{F" + color + "}" + text + "%{F-}"

forground = "#F0C674"
blue = "#61AFEF"

app_password = get_op_value("op://Private/ghcal-app-password/password")
username = get_op_value("op://Private/ghcal-app-password/username")

url = f"https://www.google.com/calendar/dav/{username}/events"

fetch_ical_file(app_password, username, url)

es = get_todays_events(sort_by_date)

next_up = None

for event in es:
    if event.start is None:
        continue

    if event.start < datetime.now(tz=tz.tzlocal()):
        continue

    time_until_start = event.start - datetime.now(tz=tz.tzlocal())
    minutes_until_start = time_until_start.total_seconds() / 60
    
    if next_up is None:
        time_until_start = event.start - datetime.now(tz=tz.tzlocal())
        human_time = naturaltime(event.start).replace(" from now", "")
        if minutes_until_start < 5:
            next_up = f"  %{{B#FF0000}}%{{F#FFFFFF}}󰃰 '{event.summary}' in {human_time}%{{F-}}%{{B-}}"
        else:
            next_up = f"  󰃰 '{format_color(forground, event.summary or '')}' in {format_color(blue, human_time)}"

    if minutes_until_start < 2:
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
        
        if minutes_until_start < 1:
            blinkStickClient.blink(name="red", repeats=7, delay=1000)

print(next_up)
