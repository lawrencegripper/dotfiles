#!/usr/bin/python3

import apt_pkg
import apt
import json
import os
import subprocess
import sys
from typing import List, Optional, Tuple
from datetime import datetime, timedelta

def get_available_updates_apt_pkg() -> Tuple[List[str], bool]:
    try:
        apt_pkg.init_config()
        apt_pkg.init_system()
        
        cache = apt.Cache()
        cache.open()
        
        updates = []
        for package in cache:
            if package.is_upgradable:
                # Skip packages that are deferred due to phasing
                if package.phasing_applied:
                    continue
                candidate = package.candidate
                installed = package.installed
                if candidate and installed:
                    update_info = f"{package.name}/{candidate.architecture} {candidate.version} [upgradable from: {installed.version}]"
                    updates.append(update_info)
        
        return updates, True
    except Exception as e:
        return [], False

def get_security_updates(updates: List[str]) -> List[str]:
    """Get list of security updates from the available updates"""
    security_updates = []
    for update in updates:
        if 'security' in update.lower():
            security_updates.append(update)
    return security_updates

def launch_update_terminal():
    """Launch wezterm and run update-linux command"""
    try:
        subprocess.Popen([
            'wezterm', 'start', '--', 'update-linux'
        ], start_new_session=True)
        return True
    except Exception:
        return False

def get_update_icon(count: int, has_security: bool) -> str:
    """Get icon based on update status"""
    if has_security:
        return '🔒'  # Security updates available
    elif count > 0:
        return '📦'  # Regular updates available
    else:
        return '✅'  # System up to date

def get_update_color(count: int, has_security: bool) -> str:
    """Get color based on update status"""
    if has_security:
        return '#ff5555'  # Red for security updates
    elif count > 10:
        return '#ffb86c'  # Orange for many updates
    elif count > 0:
        return '#f1fa8c'  # Yellow for some updates
    else:
        return '#50fa7b'  # Green for up to date
    

def format_package_line(package_line: str) -> str:
    """Format a package line for better display in tooltip"""
    try:
        # Extract package name and versions
        parts = package_line.split()
        if len(parts) >= 2:
            package_name = parts[0].split('/')[0]
            version_info = ' '.join(parts[1:])
            return f"• {package_name}: {version_info}"
        return f"• {package_line}"
    except:
        return f"• {package_line}"

def main():
    updates, check_successful = get_available_updates_apt_pkg()
    security_updates = get_security_updates(updates)
    
    update_count = len(updates)
    has_security = len(security_updates) > 0
    
    icon = get_update_icon(update_count, has_security)
    color = get_update_color(update_count, has_security)
    
    # Create status text
    if not check_successful:
        status_text = "Update Check Failed"
        class_name = "updates-error"
    elif update_count == 0:
        status_text = "Up to Date"
        class_name = "updates-current"
    else:
        status_text = f"{update_count} Update{'s' if update_count != 1 else ''}"
        subprocess.run([
                "notify-send",
                "--urgency=normal",
                "--app-name=Uptime Kuma",
                "Updates Available",
                status_text
            ], check=True)
        if has_security:
            status_text += " (Security)"
            class_name = "updates-security"
        else:
            class_name = "updates-available"
    
    # Format output text
    output = f'<span font_weight="bold"> <span color="{color}">󰏔</span> {status_text} {icon}</span>'
    
    # Create detailed tooltip
    if not check_successful:
        tooltip = '<b>Update Check Failed</b>\n\nCould not check for updates.\nTry running manually or check your connection.\n\n<i>Click to launch update terminal</i>'
    elif update_count == 0:
        tooltip = '<b>System Up to Date</b>\n\nNo package updates available.\n\n<i>Click to launch update terminal anyway</i>'
    else:
        tooltip_lines = [f'<b>Package Updates Available: {update_count}</b>']
        
        if has_security:
            tooltip_lines.append('\n<span color="#ff5555"><b>⚠️  SECURITY UPDATES AVAILABLE</b></span>')
        
        tooltip_lines.append('\n<b>Packages to update:</b>')
        
        # Show first 15 packages, then indicate if there are more
        display_updates = updates[:15]
        for update in display_updates:
            tooltip_lines.append(format_package_line(update))
        
        if len(updates) > 15:
            tooltip_lines.append(f'... and {len(updates) - 15} more packages')
        
        if security_updates:
            tooltip_lines.append('\n<b>Security Updates:</b>')
            for sec_update in security_updates[:5]:  # Show first 5 security updates
                tooltip_lines.append(f'• {sec_update}')
            if len(security_updates) > 5:
                tooltip_lines.append(f'... and {len(security_updates) - 5} more security updates')
        
        tooltip_lines.append('\n<i>Click to launch update terminal (wezterm + update-linux)</i>')
        tooltip = '\n'.join(tooltip_lines)
    
    waybar_data = {
        'text': output,
        'tooltip': tooltip,
        'class': class_name
    }
    
    print(json.dumps(waybar_data))
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        error_data = {
            'text': f'<span color="#ff5555">⚠️ Updates</span>',
            'tooltip': f'Error checking for updates: {str(e)}\n\n<i>Click to launch update terminal</i>',
            'class': 'updates-error'
        }
        print(json.dumps(error_data))
        sys.stdout.flush()