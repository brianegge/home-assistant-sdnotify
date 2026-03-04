# systemd Notify for Home Assistant

A Home Assistant integration that sends systemd watchdog and ready notifications. If Home Assistant freezes, systemd's watchdog will automatically restart the service.

## Installation

### HACS (Recommended)

1. Open [HACS](https://hacs.xyz/) in Home Assistant
2. Go to **Integrations** and click the three-dot menu
3. Select **Custom repositories** and add:
   - Repository: `brianegge/home-assistant-sdnotify`
   - Category: Integration
4. Click **Download** on the sdnotify card
5. Restart Home Assistant

### Manual

1. Copy `custom_components/sdnotify/` to your `config/custom_components/sdnotify/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **systemd Notify** and click it
3. Click **Submit** to confirm

No YAML configuration is needed.

## systemd Setup

Your systemd unit file (e.g., `/etc/systemd/system/homeassistant.service`) should include watchdog settings:

```ini
[Unit]
Description=Home Assistant
After=network-online.target

[Service]
Type=notify
Environment=WATCHDOG_USEC=5000000
User=homeassistant
WorkingDirectory=/home/homeassistant/.homeassistant
ExecStart=/srv/homeassistant/bin/hass -c "/home/homeassistant/.homeassistant"
WatchdogSec=20
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then reload systemd:

```sh
sudo systemctl daemon-reload
sudo systemctl restart homeassistant.service
```

## How It Works

The integration creates a binary sensor that:
- Sends `READY=1` to systemd when Home Assistant has started
- Periodically sends `WATCHDOG=1` pings (interval based on `WATCHDOG_USEC` env var, default 5 seconds)
- Shows as a **problem** sensor until the ready notification is sent

If `WATCHDOG_USEC` is not set (i.e., not running under systemd), the sensor will not poll.

## Removal

1. Go to **Settings** > **Devices & Services**
2. Find **systemd Notify** and click the three-dot menu
3. Select **Delete**
4. Optionally uninstall via HACS

## Credit

Originally based on https://gist.github.com/yottatsa/2395de4ea665fecabf1dfb63796a546b
