#!/bin/bash
# GivEnergy Advanced Detailed Popup

# Ensure we have yad for better dialog display
if ! command -v yad &> /dev/null; then
    # If yad is not available, fall back to zenity
    if ! command -v zenity &> /dev/null; then
        notify-send "GivEnergy" "Please install yad or zenity for dialog display"
        exit 1
    fi
    
    # Get data and show simple zenity dialog
    DATA=$(~/.config/waybar/givenergy.py)
    TOOLTIP=$(echo "$DATA" | jq -r '.tooltip')
    zenity --info --title="GivEnergy System Status" --text="$TOOLTIP" --width=500 --height=400
    exit 0
fi

# Get fresh data from the inverter
OUTPUT=$(~/.config/waybar/givenergy.py)

# Check if we got valid JSON output
if ! echo "$OUTPUT" | jq '.' &>/dev/null; then
    yad --error --title="GivEnergy Error" --text="Failed to get data from inverter" --width=300
    exit 1
fi

# Extract data using jq
SOLAR_POWER=$(echo "$OUTPUT" | jq -r '.alt' | grep -o "Solar: [0-9]*W" | cut -d' ' -f2 | sed 's/W//')
HOME_POWER=$(echo "$OUTPUT" | jq -r '.alt' | grep -o "Home: [0-9]*W" | cut -d' ' -f2 | sed 's/W//')
BATT_PCT=$(echo "$OUTPUT" | jq -r '.alt' | grep -o "Batt: [0-9]*%" | cut -d' ' -f2 | sed 's/%//')
IS_SURPLUS=$(echo "$OUTPUT" | jq -r '.class' | grep -o "surplus")

# Extract more details from tooltip
TOOLTIP=$(echo "$OUTPUT" | jq -r '.tooltip')
GRID_STATUS=$(echo "$TOOLTIP" | grep "Status: " | grep -v "Battery" | awk '{print $2}')
BATT_STATUS=$(echo "$TOOLTIP" | grep "Status: " | grep -A1 "BATTERY" | awk '{print $2}' | tail -n1)
BATT_POWER=$(echo "$TOOLTIP" | grep "Current: " | grep -A1 "BATTERY" | awk '{print $2}' | tail -n1)
GRID_POWER=$(echo "$TOOLTIP" | grep "Current: " | grep -A1 "GRID" | awk '{print $2}' | tail -n1)
PV1_POWER=$(echo "$TOOLTIP" | grep "PV1: " | awk '{print $2}')
PV2_POWER=$(echo "$TOOLTIP" | grep "PV2: " | awk '{print $2}')
BATT_TEMP=$(echo "$TOOLTIP" | grep "Temp: " | awk '{print $2}')

# Status icons
if [ -n "$IS_SURPLUS" ]; then
    STATUS_ICON="emblem-default"
    STATUS_COLOR="#2d862d"
    HEADER_BG="#2d862d"
else
    STATUS_ICON="emblem-important"
    STATUS_COLOR="#b30000"
    HEADER_BG="#b30000"
fi

# Create a beautiful HTML report with SVG graphics
HTML_CONTENT="<html><head>
<style>
body {
    font-family: 'Ubuntu', 'Segoe UI', sans-serif;
    background-color: #1a1a1a;
    color: #f0f0f0;
    margin: 0;
    padding: 0;
}
.header {
    background-color: ${HEADER_BG};
    color: white;
    padding: 15px;
    text-align: center;
    border-bottom: 2px solid #555;
}
.container {
    padding: 20px;
}
.gauge-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.gauge {
    text-align: center;
    margin: 10px;
}
.status-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-gap: 15px;
    margin-top: 20px;
}
.status-card {
    background-color: #2a2a2a;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
.value {
    font-size: 24px;
    font-weight: bold;
}
.label {
    font-size: 14px;
    color: #aaa;
}
.solar-surplus {
    color: #2d862d;
}
.solar-deficit {
    color: #b30000;
}
</style>
</head><body>
<div class='header'>
    <h2>GivEnergy Solar System Status</h2>
</div>
<div class='container'>
    <div class='gauge-container'>
        <div class='gauge'>
            <svg width='120' height='120' viewBox='0 0 120 120'>
                <circle cx='60' cy='60' r='50' fill='none' stroke='#444' stroke-width='10'/>
                <circle cx='60' cy='60' r='50' fill='none' stroke='#ffcc00' stroke-width='10'
                        stroke-dasharray='${BATT_PCT*3.14}' stroke-dashoffset='0'
                        transform='rotate(-90 60 60)'/>
                <text x='60' y='65' font-size='24' text-anchor='middle' fill='white'>${BATT_PCT}%</text>
            </svg>
            <div class='label'>Battery Level</div>
        </div>
    </div>
    
    <div class='status-grid'>
        <div class='status-card'>
            <div class='label'>Solar Production</div>
            <div class='value solar-surplus'>${SOLAR_POWER}W</div>
            <div class='label'>PV1: ${PV1_POWER} | PV2: ${PV2_POWER}</div>
        </div>
        <div class='status-card'>
            <div class='label'>Home Consumption</div>
            <div class='value solar-deficit'>${HOME_POWER}W</div>
        </div>
        <div class='status-card'>
            <div class='label'>Battery</div>
            <div class='value'>${BATT_STATUS} (${BATT_POWER})</div>
            <div class='label'>Temperature: ${BATT_TEMP}</div>
        </div>
        <div class='status-card'>
            <div class='label'>Grid</div>
            <div class='value'>${GRID_STATUS} (${GRID_POWER})</div>
        </div>
    </div>
</div>
</body></html>"

# Show the HTML content in a YAD dialog
echo "$HTML_CONTENT" | yad --html --title="GivEnergy Solar Status" --width=600 --height=500 \
    --button="Close:0" --center --window-icon="$STATUS_ICON" \
    --borders=10 --no-buttons

exit 0
