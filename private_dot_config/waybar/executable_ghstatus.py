#!/usr/bin/env -S uv run --with PyQt5 --script

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests",
# ]
# ///

import json
import os
import pickle
import subprocess
from dataclasses import dataclass
from typing import Optional
import requests


CACHE_DIR = "/tmp/ghstatus"
CACHE_FILE = os.path.join(CACHE_DIR, "last_status.pkl")

def send_notification(title: str, body: str):
    """Send a desktop notification via notify-send"""
    try:
        subprocess.run([
            "notify-send",
            "--urgency=normal",
            "--app-name=GitHub Status",
            title,
            body
        ], check=True)
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available

def load_last_status() -> Optional[str]:
    """Load the last cached status description"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return None
    return None

def save_status(description: str):
    """Save the current status description to cache"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(description, f)

def main():
    response = requests.get("https://www.githubstatus.com/api/v2/status.json")
    if response.status_code == 200:
        @dataclass
        class Page:
            id: str
            name: str
            url: str
            time_zone: str
            updated_at: str

        @dataclass
        class Status:
            indicator: str
            description: str

        @dataclass
        class GithubStatus:
            page: Page
            status: Status

        # Parse the JSON response
        data = json.loads(response.content)
        status_data = GithubStatus(
            page=Page(
                id=data['page']['id'],
                name=data['page']['name'],
                url=data['page']['url'],
                time_zone=data['page']['time_zone'],
                updated_at=data['page']['updated_at']
            ),
            status=Status(
                indicator=data['status']['indicator'],
                description=data['status']['description']
            )
        )

        # Check for status change
        last_status = load_last_status()
        current_status = status_data.status.description
        
        if last_status is not None and last_status != current_status:
            # Status has changed, send notification
            send_notification(
                "GitHub Status Changed",
                f"Status changed from '{last_status}' to '{current_status}'"
            )
        
        # Save current status
        save_status(current_status)

        indicator_value = status_data.status.indicator if status_data.status.indicator != "none" else ""

        output = f"""<span font_weight="bold"> <span color="#0080ff"> </span> GitHub: {status_data.status.description} {indicator_value}</span>"""
        waybar_data = {
            "text": output,
        }
        # Print the JSON object
        return json.dumps(waybar_data)
    else:
        raise Exception(f"Failed to download calendar: {response.status_code} {response.text}")


if __name__ == "__main__":
    print(main())
