#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "givenergy-modbus",
#     "myskoda"
# ]
# ///

import datetime
import sys
import json
import os
import pickle
import traceback
from givenergy_modbus.client import GivEnergyClient
from givenergy_modbus.model.plant import Plant
import asyncio
from aiohttp import ClientSession
from myskoda import MySkoda
import subprocess
import base64

CACHE_DIR = "/tmp/givenergy"
CACHE_LAST_PKL = os.path.join(CACHE_DIR, "last.pkl")

def format_wattage(input_watts: int):
    """Format wattage with appropriate units and colors based on magnitude"""
    if abs(input_watts) >= 1000:
        value = f"{input_watts/1000:.1f}kW"
    else:
        value = f"{input_watts}W"
    return value

def get_flow_icon(watts: int):
    """Return directional flow icon based on power value"""
    if watts > 0:
        return "▲"
    elif watts < 0:
        return "▼"
    else:
        return "•"

def get_battery_icon(percentage: int):
    """Return appropriate battery icon based on percentage"""
    if percentage > 90:
        return "󰁹"
    elif percentage > 75:
        return "󰂂"
    elif percentage > 50:
        return "󰂀"
    elif percentage > 25:
        return "󰁿"
    else:
        return "󰁾"

def get_inverter_status():
    """Get inverter status from GivEnergy API or use cached data"""
    try:
        # Ensure cache directory exists
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
            
        client = GivEnergyClient(host="10.0.1.254")
        p = Plant(number_batteries=1)
        client.refresh_plant(p, full_refresh=True)
        with open(CACHE_LAST_PKL, 'wb') as file:
            pickle.dump(p, file)
        return p
    except Exception as e:
        # Check if cache file exists and is recent (within 5 minutes)
        if os.path.exists(CACHE_LAST_PKL):
            print("Using cached data")
            # raise "aaaaaah"
            cache_mtime = os.path.getmtime(CACHE_LAST_PKL)
            current_time = datetime.datetime.now().timestamp()
            cache_age = current_time - cache_mtime
            print(f"Cache age: {cache_age} seconds")
            
            if cache_age < 300:  # Cache is less than 5 minutes old
                with open(CACHE_LAST_PKL, 'rb') as file:
                    p = pickle.load(file)
                    return p
        # If we get here, either the cache doesn't exist, is too old, or couldn't be loaded
        print("Error talking to inverter or cache is too old")
        raise e
    
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
    
async def get_car_status():
    async with ClientSession() as session:
        myskoda = MySkoda(session)
        await myskoda.connect(get_op_value("op://Shared/Vwgroup my skoda/username"), get_op_value("op://Shared/Vwgroup my skoda/password"))
        for vin in await myskoda.list_vehicle_vins():
            charging = await myskoda.get_charging(vin)
            status = charging.status
            if status is None:
                return "No status"
            if status.battery is None:
                return "No battery status"

            human_readable = ""
            if status.state == "CHARGING":
                human_readable = f"🔌 @ {status.charge_power_in_kw}kW"
            elif status.state == "CONNECT_CABLE":
                human_readable = f"󱐤"
            elif status.state == "READY_FOR_CHARGING":
                human_readable = f"🔌"

            return f"{status.battery.state_of_charge_in_percent}% {human_readable}"

try:
    p = get_inverter_status()
    
    # Get main power values
    pv_power = p.inverter.p_pv1 + p.inverter.p_pv2  # Solar production
    load_power = p.inverter.p_load_demand  # Home consumption
    grid_power = p.inverter.p_grid_out  # Grid import/export
    battery_power = p.inverter.p_battery  # Battery charge/discharge
    battery_percent = p.inverter.battery_percent

    # Calculate percentage of home load supplied by battery
    battery_discharge_percentage = round((battery_power / load_power) * 100) if load_power > 0 else 0
    
    # Calculate if we're currently in surplus
    solar_surplus = pv_power > load_power
    # We're using the grid
    min_load_grid = 90
    importing_from_grid = grid_power < 0
    exporting_to_grid = grid_power > min_load_grid

    # Create the output with direct styling for Waybar/Pango
    output = f'<span>'
    
    # Set the class for CSS styling based on surplus/deficit
    status_class = "solar-surplus" if solar_surplus else "solar-deficit"
    
    # Use house icon instead of "Home" text with neutral color for the wattage
    output += f'<span font_weight="bold" color="#e95420">🏡</span> {format_wattage(load_power)} '
    output += f'<span font_weight="bold">󱩳</span> {format_wattage(pv_power)} '
    
    # Add battery with appropriate icon based on percentage
    batt_icon = get_battery_icon(battery_percent)
    
    # Set battery color based on charging/discharging status
    batt_color = "#ffcc00"  # Yellow for discharging
    if battery_power < 0:  # Charging
        batt_color = "#2d862d"  # Green for charging
    elif battery_power == 0:  # Discharging
        batt_color = "#92bdff"  # Blue for idle
        
    output += f'<span color="{batt_color}" font_weight="bold">{batt_icon}</span> {battery_percent}% '

    # Add car status if available
    car_status = asyncio.run(get_car_status())
    output += f'<span font_weight="bold">🚗</span> {car_status} '
    
    # Add grid status
    grid_icon = "󰈏"
    grid_color = "#2d862d" if not importing_from_grid else "#b30000"
    output += f'<span font_weight="bold" color="{grid_color}">{grid_icon}</span> {format_wattage(abs(grid_power))} '

    main_icon = ""
    if exporting_to_grid:
        main_icon = "✅ Exporting 💵💵💵"
    elif importing_from_grid:
        main_icon = "😭 Importing"
    
    if battery_power > 0:
        main_icon += f"🔋 Battery providing ({battery_discharge_percentage}% of 🏡 load)"

    
    main_color = "#2d862d" if not importing_from_grid else "#FFFFF"
    output += f'<span color="{main_color}" font_weight="bold">{main_icon}</span>'
    
    # Close the main span
    output += '</span>'
    
    # Create a much more beautiful, rich HTML tooltip
    # Surplus/deficit information for styling
    main_bg_color = "#2d862d" if solar_surplus else "#b30000"
    surplus_text = "SURPLUS" if solar_surplus else "DEFICIT"
    
    # Calculate some percentages for visualization
    solar_percentage = min(100, int((pv_power / max(1, load_power)) * 100))
    battery_charge_width = battery_percent
        
    # Generate an HTML tooltip with CSS styling
    tooltip = f"""
{p.inverter.inverter_serial_number} GivEnergy Solar System • <span color="{main_bg_color}">{surplus_text}</span>

<b>CURRENT POWER FLOWS</b>
<span color="#ffcc00">SOLAR</span>: {format_wattage(pv_power)} ({solar_percentage}% of home use)
<span color="#e95420">HOME</span>: {format_wattage(load_power)}
<span color="{batt_color}">BATTERY</span>: {battery_percent}% ({'Charging' if battery_power < 0 else 'Discharging' if battery_power > 0 else 'Idle'}) {format_wattage(abs(battery_power))}
<span color="#92bdff">GRID</span>: {'Importing' if importing_from_grid else 'Exporting 🚀'} {format_wattage(abs(grid_power))}

<b>SOLAR DETAILS</b>
PV1: {format_wattage(p.inverter.p_pv1)} • PV2: {format_wattage(p.inverter.p_pv2)}

<b>BATTERY STATUS</b>
Charge: {battery_percent}% • Power: {format_wattage(abs(battery_power))} • Temp: {p.inverter.temp_battery}°C

# <b>INVERTER STATUS</b>
# Temp: p.inverter.temp_inverter NA °C

Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    # Output direct HTML to Waybar
    # The tooltip will be shown when clicking on the module
    # Create the JSON object for Waybar
    # Ensure json is imported at the top of the file: import json
    
    # Determine the battery animation class for the top-level class
    battery_status_class = ""
    if battery_power < 0:  # Charging
        battery_status_class = "battery-charging"
    elif battery_power > 0:  # Discharging
        battery_status_class = "battery-discharging"
    
    # Combine all classes
    combined_classes = [status_class]
    if battery_status_class:
        combined_classes.append(battery_status_class)
    
    waybar_data = {
        "text": output,
        "tooltip": tooltip,
        "class": " ".join(combined_classes),  # Multiple classes for styling
        "percentage": battery_percent # Optional: use battery percentage for progress bars etc.
    }
    # Print the JSON object
    print(json.dumps(waybar_data))
    
except Exception as e:
    # Create error output in HTML format
    error_output = '<span color="#ff0000">󰚨 Energy Error</span>'
    error_tooltip = f"Failed to retrieve energy system data:\n{traceback.format_exc()}"
    waybar_error_data = {
        "text": error_output,
        "tooltip": error_tooltip,
        "class": "solar-error"
    }
    print(json.dumps(waybar_error_data))
