# Sets reasonable macOS defaults.
#
# The original idea (and a couple settings) were grabbed from:
#   https://github.com/mathiasbynens/dotfiles/blob/master/.macos
#
# Run ./set-defaults.sh and you'll be good to go.

# Global defaults
defaults write "Apple Global Domain" AppleLanguages '("en-GB")'

# Always open everything in Finder's list view. This is important.
defaults write com.apple.Finder FXPreferredViewStyle Nlsv

# Show the ~/Library folder.
chflags nohidden ~/Library

# Set a really fast key repeat.
defaults write -g InitialKeyRepeat -int 20
defaults write NSGlobalDomain KeyRepeat -int 2

# Set the Finder prefs for showing a few different volumes on the Desktop.
defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool true
defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool true

# Run the screensaver if we're in the bottom-left hot corner.
defaults write com.apple.dock wvous-bl-corner -int 5
defaults write com.apple.dock wvous-bl-modifier -int 0

# Set workspaces
defaults write com.apple.spaces spans-displays -bool true

# Menu-World-Time config
defaults write net.fostersdownunder.Menu-World-Time items -string "Seattle/Guin\\tSeattle\\tAmerica/Los_Angeles\\tUnited States\\t47.6037757\\t-122.3307651\\t1\\tSeattle/Guin\\t16777215\\t5592405\\t5592405\\t0\\t14079702\\t14079702\\t5592405\\t5592405\\t16777215\\t16777215\\t16777215\\t0\\nMichigan(Thomas)\\tMichigan\\tAmerica/Detroit\\tUnited States\\t42.7346\\t-84.5539\\t1\\t-\\t16777215\\t5592405\\t5592405\\t0\\t14079702\\t14079702\\t5592405\\t5592405\\t16777215\\t16777215\\t16777215\\t0\\nMassach(Quinn)\\tMassachusetts\\tAmerica/New_York\\tUnited States\\t42.3586044\\t-71.062854\\t1\\tNYC Quinn\\t16777215\\t5592405\\t5592405\\t0\\t14079702\\t14079702\\t5592405\\t5592405\\t16777215\\t16777215\\t16777215\\t0\\nTexas\\tTexas\\tAmerica/Chicago\\tUnited States\\t30.2728\\t-97.7412\\t1\\tTexas/Kerry\\t16777215\\t5592405\\t5592405\\t0\\t14079702\\t14079702\\t5592405\\t5592405\\t16777215\\t16777215\\t16777215\\t0" 

# alt-tab
defaults write com.lwouis.alt-tab-macos '{
        appsToShow2 = 0;
        preferencesVersion = "6.22.0";
        screensToShow2 = 0;
        showHiddenWindows = 2;
        showHiddenWindows2 = 2;
        showMinimizedWindows = 2;
        showMinimizedWindows2 = 2;
        spacesToShow2 = 1;
        updatePolicy = 1;
        windowMaxWidthInRow = 30;
    }';