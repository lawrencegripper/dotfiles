#!/usr/bin/env -S uv run --with PyQt5 --script

import json
import subprocess
import sys
import time

def exit_node():
    try:
        exit_node = subprocess.check_output([
            "/bin/bash",
            "-c",
            "tailscale status --peers --json | jq '.ExitNodeStatus.ID as $node_id | .Peer[] | select(.ID==$node_id) | .HostName'",
        ]).decode().strip()

        if exit_node:
            return f"""Exit: {exit_node}"""
        
        return ""
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available

def running():
    try:
        return subprocess.check_output([
            "/bin/bash",
            "-c",
            "tailscale status --json | jq '.BackendState'",
        ]).decode().strip()
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available
    


def main():
    output = f"""<span font_weight="bold"> <span color="#0080ff"> </span> 󰀑 Tailscale: {running()} {exit_node()}</span>"""
    waybar_data = {
        "text": output,
    }
    # Print the JSON object
    return json.dumps(waybar_data)


if __name__ == "__main__":
    while True:
        try:
            print(main())
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({ "text": f"Error: {str(e)}", "tooltip": "Failed to retrieve tailscale status." }))
            sys.stdout.flush()
            sys.exit(1)
        time.sleep(120)  # Update every 2 minutes
