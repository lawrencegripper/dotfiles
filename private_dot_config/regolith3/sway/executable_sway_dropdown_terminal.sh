#!/bin/bash

TERM_PIDFILE="/tmp/sway_dropdown_terminal.pid"
TERM_PID="$(<"$TERM_PIDFILE")"
if swaymsg "[ pid=$TERM_PID ] scratchpad show"
then
    # If multi-monitor configuration: resize on each monitor
    swaymsg "[ pid=$TERM_PID ] resize set 100ppt , move position 0 0"
else
    echo "$$" > "$TERM_PIDFILE"
    swaymsg "for_window [ pid=$$ ] 'floating enable ; resize set 100ppt 50ppt ; move position 0 0 ; move to scratchpad ; scratchpad show'"
    exec wezterm connect unix-dropdown
fi
