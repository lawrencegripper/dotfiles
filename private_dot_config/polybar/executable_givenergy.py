#!/usr/bin/env python3

import datetime
from givenergy_modbus.client import GivEnergyClient
from givenergy_modbus.model.plant import Plant

try:
    client = GivEnergyClient(host="10.0.1.254")
    p = Plant(number_batteries=1)
    client.refresh_plant(p, full_refresh=True)

    def format_color(color: str, text: str):
        return "%{F" + color + "}" + text + "%{F-}"

    def format_wattage(input: int):
        if input > 1000:
            return f"{input/1000}Kw"
        return f"{input}w"

    def format_icon(input: str):
        return format_color("#F0C674", f" {input} ")

    surplus = p.inverter.p_load_demand < (p.inverter.p_pv1 + p.inverter.p_pv2)
    if surplus:
        lightening_color = "#2d862d"
    else:
        lightening_color = "#b30000"

    output = format_color(lightening_color, "")
    output += format_icon("") + format_wattage(p.inverter.p_load_demand)
    output += format_icon("") + format_wattage(p.inverter.p_pv1 + p.inverter.p_pv2)
    output += format_icon("") + str(p.inverter.battery_percent) + "%"
    output += format_icon("") + format_wattage(p.inverter.p_grid_out)

    print(output)
except Exception as e:
    print("Error talking to inverter")
