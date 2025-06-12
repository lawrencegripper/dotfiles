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
import traceback
from typing import Dict, Optional

CACHE_DIR = "/tmp/uptime-kuma"
STATUS_CACHE_FILE = os.path.join(CACHE_DIR, "monitor_status.pkl")
os.makedirs(CACHE_DIR, exist_ok=True)

def send_notification(title: str, body: str):
    """Send a desktop notification via notify-send"""
    try:
        subprocess.run([
            "notify-send",
            "--urgency=normal",
            "--app-name=Uptime Kuma",
            title,
            body
        ], check=True)
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available

def load_last_statuses() -> Optional[Dict[str, MonitorStatus]]:
    """Load the last cached monitor statuses"""
    if os.path.exists(STATUS_CACHE_FILE):
        try:
            with open(STATUS_CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return None
    return None

def save_statuses(statuses: Dict[str, MonitorStatus]):
    """Save the current monitor statuses to cache"""
    with open(STATUS_CACHE_FILE, 'wb') as f:
        pickle.dump(statuses, f)

def get_op_value(path):
    cache_file = os.path.join(CACHE_DIR, base64.urlsafe_b64encode(path.encode()).decode())
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return file.read().strip()
    value = subprocess.check_output(["/bin/bash", "-c", f"op read '{path}'"]).decode().strip()
    
    if value.strip():  # Only write if the value is not empty
        with open(cache_file, 'w') as file:
            file.write(value)
        os.chmod(cache_file, 0o600)
    else:
        raise ValueError(f"Value for {path} is empty or not found in 1Password")
    return value

def get_icon_for_status(status):
    """Return appropriate icon based on monitor status"""
    if status == MonitorStatus.UP:
        return "🟢"
    elif status == MonitorStatus.DOWN:
        return "🔴"
    elif status == MonitorStatus.PENDING:
        return "🟡"
    elif status == MonitorStatus.MAINTENANCE:
        return "⚪"
    else:
        return "❓"

def get_status_name(status):
    """Return human-readable status name"""
    if status == MonitorStatus.UP:
        return "UP"
    elif status == MonitorStatus.DOWN:
        return "DOWN"
    elif status == MonitorStatus.PENDING:
        return "PENDING"
    elif status == MonitorStatus.MAINTENANCE:
        return "MAINTENANCE"
    else:
        return "UNKNOWN"

def main():
    try:
        api = UptimeKumaApi(get_op_value("op://Private/uptime-kuma/website"))
        api.login(get_op_value("op://Private/uptime-kuma/username"), get_op_value("op://Private/uptime-kuma/password"))

        icon = "🟢"
        monitors = api.get_monitors()
        tooltip = f"<b>Uptime Kuma Status:</b> {icon} \n"
        
        # Load previous statuses and prepare current statuses
        last_statuses = load_last_statuses() or {}
        current_statuses = {}
        
        for monitor in monitors:
            status = api.get_monitor_status(monitor['id'])
            monitor_name = monitor['name']
            current_statuses[monitor_name] = status
            
            tooltip += f"<b>{monitor_name}</b>: {get_icon_for_status(status)} \n"
            
            if status == MonitorStatus.DOWN:
                icon = "🔴"
            
            # Check for status changes
            if monitor_name in last_statuses and last_statuses[monitor_name] != status:
                old_status = get_status_name(last_statuses[monitor_name])
                new_status = get_status_name(status)
                send_notification(
                    f"Monitor Status Changed: {monitor_name}",
                    f"Status changed from {old_status} to {new_status}"
                )
        
        # Save current statuses
        save_statuses(current_statuses)
                
        return json_output(icon, tooltip)
    except Exception as e:
        error_message = f"Error: {str(e)}"
        stack_trace = traceback.format_exc()
        return json_output("❌", f"{error_message}\n\n{stack_trace}", error="Error")


def json_output(icon, tooltip, error=None):
    output = f"""<span font_weight="bold"> <span color="#0080ff">󰒍</span> Homenet: {icon} {error}</span>"""
    waybar_data = {
        "text": output,
        "tooltip": tooltip,
    }
    
    return json.dumps(waybar_data)

if __name__ == "__main__":
    print(main())
