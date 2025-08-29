local module = {}

local wezterm = require 'wezterm'

function module.apply(config)
    -- override the transparency
    config.window_background_opacity = 0.8
    config.text_background_opacity = 1
    config.color_scheme = 'Monokai Pro (Gogh)'

    -- Run swaymsg command on startup
    wezterm.on('gui-startup', function(cmd)
        local success, stdout, stderr = wezterm.run_child_process {
            'swaymsg',
            'floating enable ; resize set 100ppt 50ppt ; move position 0 0 ; move to scratchpad ; scratchpad show'
        }
    end)
end

return module