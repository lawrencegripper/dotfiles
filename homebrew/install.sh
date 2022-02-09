#!/bin/sh
#
# Homebrew
#
# This installs some of the common dependencies needed (or at least desired)
# using Homebrew.

# Check for Homebrew
if test ! $(which brew)
then
  echo "  Installing Homebrew for you."

  # Install the correct homebrew for each OS type
  if test "$(uname)" = "Darwin"
  then
    if test $(which sudo)
    then
      info 'Makesure brews can write to zsh config'
      sudo chown -R $(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions
      chmod u+w /usr/local/share/zsh /usr/local/share/zsh/site-functions
    else
      info 'Makesure brews can write to zsh config'
      chown -R $(whoami) /usr/local/share/zsh /usr/local/share/zsh/site-functions
      chmod u+w /usr/local/share/zsh /usr/local/share/zsh/site-functions
    fi
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
  elif test "$(expr substr $(uname -s) 1 5)" = "Linux"
  then
    # cleanup 
    rm -rf /home/linuxbrew/
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /root/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  fi

fi

# Install the files from brew bundle file
if test "$CODESPACES" = "true"
then
  brew bundle --file=~/.Brewfile.codespaces -v
else 
  brew bundle --file=~/.Brewfile -v
fi

# hack install fast-cli
npm install -g fast-cli

exit 0
