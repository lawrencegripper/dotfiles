# load z into zsh
. $(brew --prefix)/etc/profile.d/z.sh
. <(azbrowse completion zsh)
. <(azbrowse completion zsh | sed 's/azbrowse/azb/g')
. <(devcontainer completion zsh)
. <(devcontainer completion zsh | sed 's/devcontainer/dc/g')
. <(kubectl completion zsh | sed 's/kubectl/k/g')
eval "$(starship init zsh)"

autoload bashcompinit && bashcompinit
source /usr/local/etc/bash_completion.d/az