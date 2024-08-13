-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices

-- config.color_scheme = 'Monokai Pro (Gogh)'
config.color_scheme = 'Material (Gogh)'
config.font_size = 18
config.font = wezterm.font('JetBrains Mono Nerd Font', { italic = false })

-- and finally, return the configuration to wezterm
return config