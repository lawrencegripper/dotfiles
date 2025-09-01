local module = {}

local wezterm = require 'wezterm'

function module.apply(config)
    -- override the transparency
    config.window_background_opacity = 0.8
    config.text_background_opacity = 1
    config.color_scheme = 'Monokai Pro (Gogh)'

    -- Run swaymsg command on startup
    -- wezterm.on('gui-attach', function(cmd)
    --     local success, stdout, stderr = wezterm.run_child_process {
    --         'swaymsg',
    --         '"floating enable ; resize set 100ppt 50ppt ; move position 0 0 ; move to scratchpad ; scratchpad show"'
    --     }
    --     if success then
    --         wezterm.log_info('Successfully ran swaymsg')
    --     else
    --         wezterm.log_error('Failed to run swaymsg: ' .. stderr)
    --     end
    -- end)

    -- wezterm.on('gui-start', function(cmd)
    --     local success, stdout, stderr = wezterm.run_child_process {
    --         'swaymsg',
    --         '"floating enable ; resize set 100ppt 50ppt ; move position 0 0 ; move to scratchpad ; scratchpad show"'
    --     }
    --     if success then
    --         wezterm.log_info('Successfully ran swaymsg')
    --     else
    --         wezterm.log_error('Failed to run swaymsg: ' .. stderr)
    --     end

    -- end)
end

return module