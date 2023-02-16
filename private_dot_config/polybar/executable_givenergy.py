#!/usr/bin/env python3

import datetime
from givenergy_modbus.client import GivEnergyClient
from givenergy_modbus.model.plant import Plant

try:
    client = GivEnergyClient(host="10.0.1.254")
    p = Plant(number_batteries=1)
    client.refresh_plant(p, full_refresh=True)

    def format_wattage(input: int):
        if input > 1000:
            return f"{input/1000}Kw"
        return f"{input}w"

    output = "%{F#ffff1a}  %{F-}"
    output += "  " + format_wattage(p.inverter.p_load_demand)
    output += " 󰶛 " + format_wattage(p.inverter.p_pv1 + p.inverter.p_pv2)
    output += "  " + str(p.inverter.battery_percent) + "%"
    output += "  " + format_wattage(p.inverter.p_grid_out)

    print(output)
except Exception as e:
    print("Error talking to inverter")
