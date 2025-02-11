local config = require('./wezterm')

config.automatically_reload_config = true

require('quake-overrides').apply(config)

return config