#!/bin/bash

if swaymsg "[ pid=$(cat "/tmp/sway_dropdown_terminal.pid") ] scratchpad show"
then
    # If multi-monitor configuration: resize on each monitor
    swaymsg "[ pid=$(cat "/tmp/sway_dropdown_terminal.pid") ] resize set 100ppt , move position 0 0"
else
    wezterm connect unix-dropdown &
    echo "$!" > "$TERM_PIDFILE"
    swaymsg "for_window [ pid=$$ ] 'floating enable ; resize set 100ppt 50ppt ; move position 0 0 ; move to scratchpad ; scratchpad show'"
fi
