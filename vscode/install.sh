if test "$CODESPACES" = "true"
then
  echo "Skipping VSCode config as in codespaces"
else
  if test "$(uname)" = "Darwin"
  then
    ln -sf "$ZSH/vscode/settings.json" "$HOME/Library/Application Support/Code/User/settings.json"
  elif test "$(expr substr $(uname -s) 1 5)" = "Linux"
  then
    ln -sf "$ZSH/vscode/settings.json" "$HOME/.var/app/com.visualstudio.code/config/Code/User/settings.json"
  fi

  if test "$(expr substr $(uname -s) 1 5)" = "Linux"
  then
    while read ex; do
      flatpak run com.visualstudio.code --install-extension $ex
    done <$ZSH/vscode/extensions.txt
  else
    while read ex; do
      code --install-extension $ex
    done <$ZSH/vscode/extensions.txt
  fi
fi
