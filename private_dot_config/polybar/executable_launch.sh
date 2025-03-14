#!/usr/bin/env bash

# Terminate already running bar instances
# If all your bars have ipc enabled, you can use 
polybar-msg cmd quit
# Otherwise you can use the nuclear option:
# killall -q polybar

# Launch bar1 and bar2
echo "---" | tee -a /tmp/polybar1.log /tmp/polybar2.log
polybar -r -c ~/.config/polybar/config.ini bar1 2>&1 | tee -a /tmp/polybar1.log &
polybar -r -c ~/.config/polybar/config.ini bar2 2>&1 | tee -a /tmp/polybar2.log &

echo "Bars launched..."
# Wait for the bars exit
wait
