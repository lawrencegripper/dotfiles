ln -sf "$ZSH/vscode/settings.json" "$HOME/Library/Application Support/Code/User/settings.json"

# Install VSCode extensions
while read ex; do
  code --install-extension $ex
done <$ZSH/vscode/extensions.txt

# Install requried local tooling
gem install solargraph # Supports castwide.solargraph
gem install rubocop