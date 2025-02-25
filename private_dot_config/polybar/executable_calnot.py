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

import os
import subprocess
import base64
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dateutil import tz
import time
import pickle
import re
from icalevents.icalevents import events, Event
from humanize import naturaltime
from PyQt5.QtWidgets import QApplication, QMessageBox
from blinkstick import blinkstick

CACHE_DIR = "/tmp/ghcal"
CACHE_ALL_EVENTS = f"{CACHE_DIR}/all.ics"
CACHE_TODAY_PKL = f"{CACHE_DIR}/today.pkl"
os.makedirs(CACHE_DIR, exist_ok=True)
os.chmod(CACHE_DIR, 0o700)

blinkStickClient = blinkstick.find_first()

def get_todays_events():
    if os.path.exists(CACHE_TODAY_PKL):
        with open(CACHE_TODAY_PKL, 'rb') as file:
            es = pickle.load(file)
    else:
        start_of_today = datetime.now(tz=tz.tzlocal()).replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today.replace(hour=23, minute=59, second=59)
        es = events(file=CACHE_ALL_EVENTS, start=start_of_today, end=end_of_today)
        with open(CACHE_TODAY_PKL, 'wb') as file:
            pickle.dump(es, file)
    es.sort(key=lambda e: e.start.astimezone() if e.start else datetime.min.replace(tzinfo=tz.tzutc()))
    return es

def get_op_value(path):
    cache_file = os.path.join(CACHE_DIR, base64.urlsafe_b64encode(path.encode()).decode())
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return file.read().strip()
    value = subprocess.check_output(["/bin/bash", "-c", f"op read '{path}'"]).decode().strip()
    with open(cache_file, 'w') as file:
        file.write(value)
    os.chmod(cache_file, 0o600)
    return value

def extract_zoom_link(event):
    text = event.description or event.location
    if not text:
        return None
    text = text.replace("<br>", "\n")
    match = re.search(r"https://.*\.zoom\.us/j/[^\s]*", text)
    if match:
        zoom_link = match.group(0)
        confno, pwd = zoom_link.split("/j/")[1].split("?pwd=")
        return f"zoommtg://zoom.us/join?action=join&confno={confno}&pwd={pwd}"
    return None

def fetch_ical_file(app_password, username, url):
    if os.path.exists(CACHE_ALL_EVENTS) and time.time() - os.path.getmtime(CACHE_ALL_EVENTS) < 300:
        return
    response = requests.get(url, auth=HTTPBasicAuth(username, app_password))
    if response.status_code == 200:
        with open(CACHE_ALL_EVENTS, "wb") as file:
            file.write(response.content)
        os.chmod(CACHE_ALL_EVENTS, 0o600)
        if os.path.exists(CACHE_TODAY_PKL):
            os.remove(CACHE_TODAY_PKL)
    else:
        raise Exception(f"Failed to download calendar: {response.status_code} {response.text}")

def format_color(color, text):
    return f"%{{F{color}}}{text}%{{F-}}"

def main():
    forground = "#F0C674"
    blue = "#61AFEF"

    app_password = get_op_value("op://Private/ghcal-app-password/password")
    username = get_op_value("op://Private/ghcal-app-password/username")
    url = f"https://www.google.com/calendar/dav/{username}/events"

    fetch_ical_file(app_password, username, url)
    es = get_todays_events()

    next_up, after_that = None, None

    for event in es:
        if not event.start or event.start < datetime.now(tz=tz.tzlocal()):
            continue

        minutes_until_start = (event.start - datetime.now(tz=tz.tzlocal())).total_seconds() / 60
        human_time = naturaltime(event.start).replace(" from now", "")
        
        display_text = f"  %{{B#FF0000}}%{{F#FFFFFF}}󰃰 '{event.summary}' in {human_time}%{{F-}}%{{B-}}"
        if minutes_until_start > 5: 
            display_text = f"  󰃰 '{format_color(forground, event.summary or '')}' in {format_color(blue, human_time)}"

        if not next_up:
            next_up = display_text
        elif not after_that:
            after_that = display_text

        if minutes_until_start < 2:
            app = QApplication([])
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Meeting Reminder")
            msg_box.setText(f"'{event.summary}' is about to start.\n\nDo you acknowledge that you might miss it?")
            msg_box.setFont(msg_box.font().setPointSize(18))
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            if msg_box.exec_() == QMessageBox.Ok:
                zoom_launch_uri = extract_zoom_link(event)
                if zoom_launch_uri:
                    subprocess.Popen(["xdg-open", zoom_launch_uri])
            if minutes_until_start < 1:
                blinkStickClient.blink(name="red", repeats=7, delay=1000)

    print(f"{next_up} {after_that}")

if __name__ == "__main__":
    main()
