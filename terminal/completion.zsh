# Enable fzf
# Setup fzf
# ---------
if [[ ! "$PATH" == */usr/local/opt/fzf/bin* ]]; then
  export PATH="${PATH:+${PATH}:}/usr/local/opt/fzf/bin"
fi

# Auto-completion
# ---------------
[[ $- == *i* ]] && source "/usr/local/opt/fzf/shell/completion.zsh" 2> /dev/null

# Key bindings
# ------------
source "/usr/local/opt/fzf/shell/key-bindings.zsh"
# End

# Add SSH key
if test "$(uname)" = "Darwin"
then
  ssh-add --apple-use-keychain ~/.ssh/id_ed25519
  ssh-add --apple-use-keychain ~/.ssh/id_rsa_gh
fi