# load z into zsh
. $(brew --prefix)/etc/profile.d/z.sh
. <(azbrowse completion zsh)
. <(azbrowse completion zsh | sed 's/azbrowse/azb/g')
. <(devcontainer completion zsh)
. <(devcontainer completion zsh | sed 's/devcontainer/dc/g')
eval "$(starship init zsh)"