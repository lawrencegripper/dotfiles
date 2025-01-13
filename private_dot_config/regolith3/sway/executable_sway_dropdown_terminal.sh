#!/bin/bash

TERM_PIDFILE="/tmp/sway_dropdown_terminal.pid"
pid=$(cat "/tmp/sway_dropdown_terminal.pid")
echo "trying to match pid: $pid"
if swaymsg "[ pid=$pid ] scratchpad show"
then
    echo "sway found the pid"
    # If multi-monitor configuration: resize on each monitor
    swaymsg "[ pid=$(cat "/tmp/sway_dropdown_terminal.pid") ] resize set 100ppt , move position 0 0"
else
    echo "sway didn't find pid"
    rm -f "/tmp/sway_dropdown_terminal.pid"
    wezterm connect unix-dropdown > /dev/null 2>&1 &
    top_level_process=$!

    tree=$(pstree -a -T -p $top_level_process)

    # binfmt-bypass,87106 /home/linuxbrew/.linuxbrew/bin/wezterm start --cwd .
    # └─wezterm-gui,87108 start --cwd .
    #     └─zsh,87121
    #         └─wezterm-gui,88388
    #             └─zsh,88396

    wezterm_pid=$(echo "$tree" | grep "wezterm-gui" | grep -oP '\d+' | tail -n 1)

    echo "$wezterm_pid" > "$TERM_PIDFILE"
    echo "wezterm_gui_pid: $wezterm_pid"
    swaymsg "for_window [ pid=$wezterm_pid ] 'floating enable ; resize set 100ppt 50ppt ; move position 0 0 ; move to scratchpad ; scratchpad show'"
    echo "Dropdown terminal started with pid $(cat "$TERM_PIDFILE") $!"
fi