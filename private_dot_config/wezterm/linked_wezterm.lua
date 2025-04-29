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

config.enable_scroll_bar = true

-- Change mouse scroll amount https://github.com/wez/wezterm/discussions/4947
config.mouse_bindings = {
  {
    event = { Down = { streak = 1, button = { WheelUp = 1 } } },
    mods = 'NONE',
    action = act.ScrollByLine(-3),
  },
  {
    event = { Down = { streak = 1, button = { WheelDown = 1 } } },
    mods = 'NONE',
    action = act.ScrollByLine(3),
  },
}

-- Domains that can be used for stuff see: private_dot_config/regolith3/sway/executable_sway_dropdown_terminal.sh
config.unix_domains = {
  {
    name = 'unix-dropdown',
  },
}

config.use_fancy_tab_bar = true
config.hide_tab_bar_if_only_one_tab = true

-- config.color_scheme = 'Monokai Pro (Gogh)'
-- config.color_scheme = 'MaterialDesignColors'
config.color_scheme = "Ayu Mirage"
config.font_size = 11

-- See: https://github.com/githubnext/monaspace/issues/133
-- Monaspace:  https://monaspace.githubnext.com/
-- Based upon, contributed to:  https://gist.github.com/ErebusBat/9744f25f3735c1e0491f6ef7f3a9ddc3
config.freetype_load_target = 'HorizontalLcd' -- https://wezfurlong.org/wezterm/config/lua/config/freetype_load_target.html
config.font = wezterm.font(
{ -- Normal text
  family='Monaspace Neon',
  harfbuzz_features={ 'calt', 'liga', 'dlig', 'ss01', 'ss02', 'ss03', 'ss04', 'ss05', 'ss06', 'ss07', 'ss08' },
  stretch='UltraCondensed', -- This doesn't seem to do anything
  -- weight='Medium'
})

config.font_rules = {
  { -- Italic
    intensity = 'Normal',
    italic = true,
    font = wezterm.font({
      -- family="Monaspace Radon",  -- script style
      family='Monaspace Neon', -- courier-like
      style = 'Italic',
    })
  },

  { -- Bold
    intensity = 'Bold',
    italic = false,
    font = wezterm.font( {
      family='Monaspace Neon',
      family='Monaspace Neon',
      -- weight='ExtraBold',
      weight='Bold',
      })
  },

  { -- Bold Italic
    intensity = 'Bold',
    italic = true,
    font = wezterm.font( {
      family='Monaspace Neon',
      style='Italic',
      weight='Bold',
      }
    )
  },
}

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