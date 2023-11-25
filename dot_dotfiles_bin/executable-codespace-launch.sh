#!/bin/bash

NAME=$1
echo "Opening codespace $NAME"
gh cs code --codespace $NAME --insiders
# Copy auth details for atuin
gh cs cp --codespace $NAME -e ~/.local/share/atuin/session 'remote:/workspaces/atuin_session'
gh cs cp --codespace $NAME -e ~/.local/share/atuin/key 'remote:/workspaces/atuin_key'
#                                                                                  atuin server               languagetool grammer/spellcheck
kitty bash -c "export TERM=xterm-256color; gh codespace ssh --codespace $NAME -- -R 3123:100.120.65.104:80 -R 8081:localhost:8081"