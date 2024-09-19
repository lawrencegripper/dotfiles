-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()

-- This is where you actually apply your config choices

-- config.color_scheme = 'Monokai Pro (Gogh)'
config.color_scheme = 'MaterialDesignColors'
config.font_size = 18
config.font = wezterm.font('JetBrains Mono Nerd Font', { italic = false })

config.scrollback_lines = 90000

config.ssh_domains = {
    {
      -- This name identifies the domain
      name = 'libvirt',
      -- The hostname or address to connect to. Will be used to match settings
      -- from your ssh config file
      remote_address = 'libvirt',
      -- The username to use on the remote host
      username = 'lawrencegripper',
    },
  }
  

-- and finally, return the configuration to wezterm
return config