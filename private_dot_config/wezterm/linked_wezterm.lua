-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This will hold the configuration.
local config = wezterm.config_builder()
local act = wezterm.action

-- This is where you actually apply your config choices

wezterm.on('user-var-changed', function(window, pane, name, value)
  wezterm.log_info('var', name, value)
  if name == 'wez_not' then
    window:toast_notification('wezterm', 'msg: ' .. value)
  end

  if name == 'wez_copy' then
    window:copy_to_clipboard(value, 'Clipboard')
  end
end)

-- config.color_scheme = 'Monokai Pro (Gogh)'
config.color_scheme = 'MaterialDesignColors'
config.font_size = 13
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
    }
  }




-- CTRL SHIFT P to open links
-- https://github.com/wez/wezterm/issues/1362
config.keys = {
  -- Move quick select so it doesn't clash with 1 password
  {
    key = 'm',
    mods = 'CTRL|SHIFT',
    action = wezterm.action.QuickSelect, 
  },
  -- show the pane selection mode, but have it swap the active and selected panes
  {
    key = 'S',
    mods = 'CTRL',
    action = act.PaneSelect {
      mode = 'SwapWithActive',
    },
  },
  {
    key = 'w',
    mods = 'CMD|CTRL|SHIFT|ALT',
    action = wezterm.action.CloseCurrentPane { confirm = true },
  },
  -- This will create a new split and run the `top` program inside it
  {
    key = 'e',
    mods = 'CTRL|SHIFT|ALT',
    action = wezterm.action.SplitPane {
      direction = 'Up',
      -- command = { args = { 'top' } },
      size = { Percent = 50 },
    },
  },
  {
    key = 'd',
    mods = 'CTRL|SHIFT|ALT',
    action = wezterm.action.SplitPane {
      direction = 'Down',
      -- command = { args = { 'top' } },
      size = { Percent = 50 },
    },
  },
  {
    key = 's',
    mods = 'CTRL|SHIFT|ALT',
    action = wezterm.action.SplitPane {
      direction = 'Left',
      -- command = { args = { 'top' } },
      size = { Percent = 50 },
    },
  },
  {
    key = 'f',
    mods = 'CTRL|SHIFT|ALT',
    action = wezterm.action.SplitPane {
      direction = 'Right',
      -- command = { args = { 'top' } },
      size = { Percent = 50 },
    },
  },
  {
    key="Y", mods="CTRL",
     action=wezterm.action{QuickSelectArgs={
       patterns={
          "https?://\\S+"
       },
       action = wezterm.action_callback(function(window, pane)
          local url = window:get_selection_text_for_pane(pane)
          wezterm.log_info("opening: " .. url)
          wezterm.open_with(url)
       end)
     }}
   }, 
}

-- and finally, return the configuration to wezterm
return config