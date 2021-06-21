alias tf=terraform
alias d=docker
alias docker-remote-start="ssh -fNL localhost:23750:/var/run/docker.sock lawrence@ubuntudev && docker context use grumpet"
alias docker-remote-stop="ps aux | grep  '[l]ocalhost:23750' | awk '{print $2}' | xargs kill && docker context use local"
alias docker-remote-push="ssh lawrence@ubuntudev mkdir -p \${PWD} && rsync -rlptv --progress \${PWD} \"lawrence@ubuntudev:\${PWD}/../\""
alias docker-remote-pull="rsync -rlptv --progress \"lawrence@ubuntudev:\${PWD}\" \${PWD}/../"
alias heic-convert="ls *.heic | xargs -n 1 -I {} heif-convert {} {}.jpg"
alias dco="devcontainer open-in-code ."
alias dce="devcontainer exec"
alias k="kubectl"
alias azb=azbrowse
alias testaudio="arecord -d 10 -f cd -t wav foobar.wav && aplay foobar.wav"
alias ghrun="gh run list | grep \$(git branch --show-current) | cut -d$'\t' -f 7 | xargs gh run watch && notify-send 'Run finished'"
# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
# workaround alacritty terminfo when sshing to boxes see: https://github.com/alacritty/alacritty/issues/3360
alias ssh='TERM=xterm-256color ssh'