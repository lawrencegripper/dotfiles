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
            "tailscale status --peers --json | jq -r '.ExitNodeStatus.ID as $node_id | .Peer[] | select(.ID==$node_id) | .HostName'",
        ]).decode().strip()

        if exit_node:
            return f"""Exit: {exit_node}"""
        
        return ""
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available

def tailnet_name():
    try:
        name = subprocess.check_output([
            "/bin/bash",
            "-c",
            "tailscale status --json | jq -r '.Self.CapMap[\"tailnet-display-name\"][0]'",
        ]).decode().strip()
        
        if name and name != "null":
            if name.endswith("@hotmail.co.uk"):
                name = "homenet"
            if name.endswith(".com"):
                name = "work"
            return f"{name}"
        
        return ""
    except subprocess.CalledProcessError:
        pass  # Fail silently if not available

def running():
    try:
        state = subprocess.check_output([
            "/bin/bash",
            "-c",
            "tailscale status --json | jq -r '.BackendState'",
        ]).decode().strip()

        if state == "Running":
            return "✅"
    except subprocess.CalledProcessError:
        pass  # Fail silently if notify-send is not available

def handle_click():
    """Handle click event to toggle between work and homenet tailnets"""
    if len(sys.argv) > 1 and sys.argv[1] == 'click':
        current_tailnet = tailnet_name()
        
        # Determine which tailnet to switch to
        if current_tailnet == "work":
            target_tailnet = "homenet"
        elif current_tailnet == "homenet":
            target_tailnet = "work"
        
        try:
            # Use wezterm to run sudo tailscale switch command and signal waybar to refresh
            subprocess.run([
                '/bin/bash', '-c', 
                f'echo "auth {current_tailnet} -> {target_tailnet}" && sudo tailscale switch {target_tailnet} && echo "Successfully switched to {target_tailnet}" && pkill -RTMIN+11 waybar && sleep 2'
            ], check=False)  # Don't check return code since wezterm will handle the command
            
            # Send notification about tailnet switch attempt
            try:
                subprocess.run([
                    'notify-send',
                    '--urgency=normal',
                    '--app-name=Tailscale',
                    'Tailnet Switch Started',
                    f'Opening terminal to switch to: {target_tailnet}'
                ], check=False)
            except:
                pass
                
        except Exception as e:
            # Send error notification
            try:
                subprocess.run([
                    'notify-send',
                    '--urgency=critical',
                    '--app-name=Tailscale',
                    'Tailnet Switch Failed',
                    f'Failed to open terminal for switching to {target_tailnet}: {e}'
                ], check=False)
            except:
                pass
        
        sys.exit(0)
    return False
    


def main():
    # Handle click events
    if handle_click():
        return
    
    current_tailnet = tailnet_name()
    current_exit_node = exit_node()
    current_status = running()
    
    output = f"""<span font_weight="bold"> <span color="#0080ff"> </span> 󰀑 Tailscale: {current_status} {current_tailnet} {current_exit_node}</span>"""
    
    # # Create tooltip with current status and instructions
    # tooltip_lines = ['<b>Tailscale Status:</b>']
    # tooltip_lines.append(f'Status: {current_status}')
    # tooltip_lines.append(f'Tailnet: {current_tailnet}')
    # if current_exit_node:
    #     tooltip_lines.append(f'{current_exit_node}')
    # tooltip_lines.append('')
    # tooltip_lines.append('<i>Click to toggle between work and homenet</i>')
    # tooltip = '\n'.join(tooltip_lines)
    
    waybar_data = {
        "text": output,
        # "tooltip": tooltip
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
