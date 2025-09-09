local config = require('./wezterm')

config.automatically_reload_config = true

config.unix_domains = {
    {
        name='CS_NAME',
        proxy_command = {
            '/home/linuxbrew/.linuxbrew/bin/gh', 'cs', 'ssh', '-c', 'CS_NAME',
            '--',
            -- Port forwarding
            '-R', '3123:atuin-api.unicorn-tailor.ts.net:80',
            '-R', '8123:languagetool-api.unicorn-tailor.ts.net:8123',
            -- Wezterm proxy
            'wezterm', 'cli', 'proxy'
        }
    }
}


return config