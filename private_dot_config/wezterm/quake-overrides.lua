local module = {}

function module.apply(config)
    -- override the transparency
    config.window_background_opacity = 0.8
    config.text_background_opacity = 1
    config.color_scheme = 'Monokai Pro (Gogh)'
end

return module