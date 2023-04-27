#!/bin/bash

rm -f ~/.gh-notifications
if type "op" > /dev/null; then
    op read "op://Personal/github.com/PATS/gh-notifications" > ~/.config/gh-notifications
    chmod 600 ~/.config/gh-notifications
else
    echo "Failed not available"
fi
