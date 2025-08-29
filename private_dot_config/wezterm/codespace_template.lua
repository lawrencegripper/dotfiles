local config = require('./wezterm')

config.automatically_reload_config = true

config.unix_domains = {
    {
        name='CS_NAME',
        proxy_command = { '/home/linuxbrew/.linuxbrew/bin/gh', 'cs', 'ssh', '-c', 'CS_NAME', '--', '-R', '3123:100.110.255.124:80', '-R', '8123:languagetool-api.unicorn-tailor.ts.net:8123', 'wezterm', 'cli', 'proxy' }
    }
}


return config