#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional

def get_available_profiles() -> List[str]:
    """Get list of available power profiles"""
    try:
        result = subprocess.run(['powerprofilesctl', 'list'], 
                              capture_output=True, text=True, check=True)
        profiles = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line and ':' in line and not line.startswith(' '):
                profile = line.split(':')[0].strip()
                if profile and profile not in ['CpuDriver', 'PlatformDriver', 'Degraded']:
                    profiles.append(profile.replace('*', '').strip())
        return profiles if profiles else ['performance', 'balanced', 'power-saver']
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to common profiles if powerprofilesctl fails
        return ['performance', 'balanced', 'power-saver']

def get_current_profile() -> str:
    """Get the current active power profile"""
    try:
        result = subprocess.run(['powerprofilesctl', 'get'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try to detect from /sys if powerprofilesctl fails
        try:
            with open('/sys/firmware/acpi/platform_profile', 'r') as f:
                profile = f.read().strip()
                # Map common platform profile names to powerprofiles names
                mapping = {
                    'low-power': 'power-saver',
                    'quiet': 'power-saver',
                    'cool': 'power-saver',
                    'balanced': 'balanced',
                    'performance': 'performance'
                }
                return mapping.get(profile, profile)
        except:
            return 'balanced'  # Default fallback

def set_next_profile() -> str:
    """Cycle to the next power profile"""
    available = get_available_profiles()
    current = get_current_profile()
    
    try:
        current_index = available.index(current)
        next_index = (current_index + 1) % len(available)
        next_profile = available[next_index]
        
        subprocess.run(['powerprofilesctl', 'set', next_profile], 
                      check=True, capture_output=True)
        return next_profile
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return current

def get_profile_icon(profile: str) -> str:
    """Get icon for power profile"""
    icons = {
        'performance': '⚡',
        'balanced': '⚖️',
        'power-saver': '🔋'
    }
    return icons.get(profile, '⚙️')

def get_profile_color(profile: str) -> str:
    """Get color for power profile"""
    colors = {
        'performance': '#ff5555',
        'balanced': '#f1fa8c', 
        'power-saver': '#50fa7b'
    }
    return colors.get(profile, '#bd93f9')

def handle_click():
    """Handle click event to cycle profiles"""
    if len(sys.argv) > 1 and sys.argv[1] == 'click':
        new_profile = set_next_profile()

        # Signal waybar to refresh the module
        subprocess.run(['pkill', '-RTMIN+9', 'waybar'], check=False)

        # Send notification about profile change
        try:
            subprocess.run([
                'notify-send',
                '--urgency=normal',
                '--app-name=Power Profile',
                'Power Profile Changed',
                f'Switched to: {new_profile}'
            ], check=False)
        except:
            pass
        return True
    return False

def main():
    # Handle click events
    if handle_click():
        return
    
    current_profile = get_current_profile()
    available_profiles = get_available_profiles()
    icon = get_profile_icon(current_profile)
    color = get_profile_color(current_profile)
    
    # Create tooltip with all available profiles
    tooltip_lines = ['<b>Power Profiles:</b>']
    for profile in available_profiles:
        indicator = '●' if profile == current_profile else '○'
        profile_icon = get_profile_icon(profile)
        tooltip_lines.append(f'{indicator} {profile_icon} {profile.title()}')
    
    tooltip_lines.append('\n<i>Click to cycle through profiles</i>')
    tooltip = '\n'.join(tooltip_lines)
    
    # Format output text to match other modules pattern
    output = f'<span font_weight="bold"> <span color="{color}">󰓅</span>{current_profile.title()} {icon}</span>'
    
    waybar_data = {
        'text': output,
        'tooltip': tooltip,
        'class': f'power-profile-{current_profile}'
    }
    
    print(json.dumps(waybar_data))
    sys.stdout.flush()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        error_data = {
            'text': f'<span color="#ff5555">⚠️ Power</span>',
            'tooltip': f'Error: {str(e)}'
        }
        print(json.dumps(error_data))
        sys.stdout.flush()