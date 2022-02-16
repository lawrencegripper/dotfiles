if test "$CODESPACES" = "true"
then
  echo "Skipping VSCode config as in codespaces"
else
  if test "$(uname)" = "Darwin"
  then
    ln -sf "$ZSH/vscode/settings.json" "$HOME/Library/Application Support/Code/User/settings.json"
  elif test "$(expr substr $(uname -s) 1 5)" = "Linux"
  then
    sudo snap install code --classic 
    mkdir -p $HOME/.config/Code/User/
    ln -sf "$ZSH/vscode/settings.json" "$HOME/.config/Code/User/settings.json"
  fi

  while read ex; do
    code --install-extension $ex
  done <$ZSH/vscode/extensions.txt
fi
