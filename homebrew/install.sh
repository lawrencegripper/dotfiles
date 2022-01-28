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
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

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
