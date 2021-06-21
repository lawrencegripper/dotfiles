# load z into zsh
. $(brew --prefix)/etc/profile.d/z.sh

# autocomplete for brew bash stuff
autoload bashcompinit && bashcompinit
if [ -f $(brew --prefix)/etc/bash_completion ]; then
    . $(brew --prefix)/etc/bash_completion
fi

# Below favour the most recent completions from the clis rather than static files
# small cost to pay at startup of terminal for this but means always up to date
# autocomplete for k
. <(kubectl completion zsh)
complete -F __start_kubectl k

# autocomplete for cobra based utils
. <(azbrowse completion zsh)
compdef _azbrowse azbrowse
. <(devcontainer completion zsh)
compdef _devcontainer devcontainer

eval "$(starship init zsh)"

# wire up rbenv
eval "$(rbenv init -)"