#!/bin/bash

if swaymsg -t get_tree | grep -q wezdrop;
then
    swaymsg "[ app_id=wezdrop ] scratchpad show"
else
    wezterm --config-file ~/.config/wezterm/quake.lua connect --class "wezdrop" unix-dropdown > /dev/null 2>&1 &
fi
