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
alias startcam="gphoto2 --stdout --capture-movie | ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video6"
alias enablecam="sudo modprobe v4l2loopback exclusive_caps=1 max_buffers=2"
alias ghrun="gh run list | grep $(git branch --show-current) | cut -d$'\t' -f 8 | xargs gh run watch && notify-send 'Run finished'"
# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'