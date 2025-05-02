#!/usr/bin/env -S uv run --with PyQt5 --script

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
#     "uptime-kuma-api"
# ]
# ///

import base64
import os
import subprocess
import requests
import json
from uptime_kuma_api import UptimeKumaApi, MonitorType, MonitorStatus
import pickle
import time

CACHE_DIR = "/tmp/uptime-kuma"
os.makedirs(CACHE_DIR, exist_ok=True)

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

def get_monitors(api):
    import os.path
    
    cache_file = os.path.join(CACHE_DIR, "monitors.pkl")
    cache_valid_seconds = 300  # 5 minutes
    
    # Check if cache exists and is still valid
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < cache_valid_seconds:
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError):
                pass  # If there's an error loading cache, continue to fetch data
    
    # Fetch new data
    monitors = api.get_monitors()
    
    # Cache the result
    with open(cache_file, 'wb') as f:
        pickle.dump(monitors, f)
    
    return monitors


def main():
    api = UptimeKumaApi(get_op_value("op://Private/uptime-kuma/website"))
    api.login(get_op_value("op://Private/uptime-kuma/username"), get_op_value("op://Private/uptime-kuma/password"))

    icon = "🟢"
    monitors = get_monitors(api)
    tooltip = f"<b>Uptime Kuma Status:</b> {icon} /n"
    for monitor in monitors:
        status = api.get_monitor_status(monitor['id'])
        tooltip += f"<b>{monitor['name']}</b>: {status.name} /n"
        if status != MonitorStatus.UP:
            icon = "🔴"

    output = f"""<span font_weight="bold" color="#e95420"> HomeNet Status {icon} </span>"""
    waybar_data = {
        "text": output,
        "tooltip": tooltip,
    }
    # Print the JSON object
    return json.dumps(waybar_data)

if __name__ == "__main__":
    print(main())

