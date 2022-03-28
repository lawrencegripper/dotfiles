# Setup fzf
# ---------
if [[ ! "$PATH" == */home/lawrencegripper/.fzf/bin* ]]; then
  export PATH="${PATH:+${PATH}:}/home/lawrencegripper/.fzf/bin"
fi

# Auto-completion
# ---------------
[[ $- == *i* ]] && source "/home/lawrencegripper/.fzf/shell/completion.bash" 2> /dev/null

# Key bindings
# ------------
source "/home/lawrencegripper/.fzf/shell/key-bindings.bash"
