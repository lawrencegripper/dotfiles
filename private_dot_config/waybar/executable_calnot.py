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
#     "psutil",
# ]
# ///

import os
import subprocess
import base64
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dateutil import tz
import time
import pickle
import re
from icalevents.icalevents import events, Event
from humanize import naturaltime
from PyQt5.QtWidgets import QApplication, QMessageBox
from blinkstick import blinkstick
import psutil

CACHE_DIR = "/tmp/ghcal"
CACHE_ALL_EVENTS = os.path.join(CACHE_DIR, "all.ics")
CACHE_TODAY_PKL = os.path.join(CACHE_DIR, "today.pkl")
SKIPPED_DIR = os.path.join(CACHE_DIR, "skipped")
JOINED_DIR = os.path.join(CACHE_DIR, "joined")
os.makedirs(CACHE_DIR, exist_ok=True)
os.chmod(CACHE_DIR, 0o700)
os.makedirs(SKIPPED_DIR, exist_ok=True)
os.makedirs(JOINED_DIR, exist_ok=True)

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
        try:
            confno, pwd = zoom_link.split("/j/")[1].split("?pwd=")
            return f"zoommtg://zoom.us/join?action=join&confno={confno}&pwd={pwd}"
        except ValueError:
            confno = zoom_link.split("/j/")[1].split("?")[0]
            return f"zoommtg://zoom.us/join?action=join&confno={confno}"
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
    return f'<span color="{color}">{text}</span>'

def format_background_color(color, text):
    return f'<span background="{color}">{text}</span>'

def prompt_to_join(event, zoom_launch_uri):
    if has_joined(event, zoom_launch_uri) or has_skipped(event, zoom_launch_uri):
        return
    app = QApplication([])
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("Meeting Reminder")
    msg_box.setText(f"'{event.summary}' is about to start.\n\nDo you acknowledge that you might miss it?")
            # msg_box.setFont(msg_box.font().setPointSize(18))
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg_box.addButton("Ignore for now", QMessageBox.NoRole)
    if msg_box.exec_() == QMessageBox.Ok:
        if zoom_launch_uri:
            subprocess.Popen(["xdg-open", zoom_launch_uri])
            mark_joined(event, zoom_launch_uri)
    elif msg_box.exec_() == QMessageBox.Cancel and zoom_launch_uri:
        mark_skipped(event, zoom_launch_uri)

def mark_skipped(event, zoom_launch_uri):
    skipped_file = os.path.join(SKIPPED_DIR, base64.urlsafe_b64encode(zoom_launch_uri.encode()).decode())
    with open(skipped_file, 'w') as file:
        file.write(f"Skipped: {event.summary} at {datetime.now(tz=tz.tzlocal())}")

def has_skipped(event, zoom_launch_uri):
    skipped_file = os.path.join(SKIPPED_DIR, base64.urlsafe_b64encode(zoom_launch_uri.encode()).decode())
    return os.path.exists(skipped_file)

def mark_joined(event, zoom_launch_uri):
    joined_file = os.path.join(JOINED_DIR, base64.urlsafe_b64encode(zoom_launch_uri.encode()).decode())
    with open(joined_file, 'w') as file:
        file.write(f"Joined: {event.summary} at {datetime.now(tz=tz.tzlocal())}")

def has_joined(event, zoom_launch_uri):
    joined_file = os.path.join(JOINED_DIR, base64.urlsafe_b64encode(zoom_launch_uri.encode()).decode())
    return os.path.exists(joined_file)

def main():
    forground = "#F0C674"
    blue = "#61AFEF"

    app_password = get_op_value("op://Private/ghcal-app-password/password")
    username = get_op_value("op://Private/ghcal-app-password/username")
    url = f"https://www.google.com/calendar/dav/{username}/events"

    fetch_ical_file(app_password, username, url)
    es = get_todays_events()

    joined, next_up, after_that = None, None, None

    for event in es:
        if not event.start or not event.end:
            continue

        # Find out if we're in a meeting atm
        if event.start < datetime.now(tz=tz.tzlocal()) - timedelta(minutes=30) and event.end < datetime.now(tz=tz.tzlocal()):
            continue

        minutes_until_start = (event.start - datetime.now(tz=tz.tzlocal())).total_seconds() / 60
        human_time = naturaltime(event.start).replace(" from now", "")

        zoom_launch_uri = extract_zoom_link(event)

        # Should we be in a meeting already?
        if zoom_launch_uri and event.start < (datetime.now(tz=tz.tzlocal())):
            if has_joined(event, zoom_launch_uri):
                # Your in the meeting already
                joined = format_background_color("#006400", f"󰏽 '{format_color(forground, event.summary or '')}'")
                continue
            if has_skipped(event, zoom_launch_uri):
                joined = format_background_color("#FFFF00", f"   Skipped '{format_color(forground, event.summary or '')}'")
            else:
                # Zoom Meeting already started but you haven't joined
                joined = format_background_color("#FF0000", f"   Missing! '{format_color(forground, event.summary or '')}'")
                blinkStickClient.blink(name="red", repeats=10, delay=100)
                prompt_to_join(event, zoom_launch_uri)
        
        # What meetings are coming up?
        if event.start < (datetime.now(tz=tz.tzlocal())):
            continue

        display_text = f"  {format_background_color('#FF0000', format_color('#FFFFFF', f"󰃰 '{event.summary}' in {human_time}"))}"
        if minutes_until_start > 5: 
            display_text = f"  󰃰 '{format_color(forground, event.summary or '')}' in {format_color(blue, human_time)}"

        if not next_up:
            next_up = display_text
        elif not after_that:
            after_that = display_text

        if minutes_until_start < 3:
            blinkStickClient.blink(name="yellow", repeats=7, delay=500)

        if minutes_until_start < 1 and zoom_launch_uri and not has_joined(event, zoom_launch_uri):
            prompt_to_join(event, zoom_launch_uri)

    if joined:
        print(f"{joined} {next_up}")
    elif next_up:
        print(f"{next_up} {after_that}")
    else: 
        print("📆 No more events today 🥳")

if __name__ == "__main__":
    # try:
        main()
    # except Exception as e:
    #     print(f"Error: {e}")

