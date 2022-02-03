## systemd notifier

Adds device to integrate with systemd service, notifying both watchdog and startup. My home assistant installation froze more than one time, so I added the watchdog to kick the service if it does.

## Setup Process

1. Install using [HACS](https://github.com/hacs/integration) or manually copy the files
2. Add sdnotify to your configuration.yaml
3. Update systemd config
4. Restart Home Assistant

## Step 1: Installation

### Installation with Home Assistant Community Store (HACS)

For easy updates whenever a new version is released, use the [Home Assistant Community Store (HACS)](https://github.com/hacs/integration) and add the following Integration in the Settings tab:

```
brianegge/home-assistant-sdnotify
```

## Step 2: Add sensor to Home Assistant's Configuration

Now that that installation and authentication are done, all that is left is to add the binary sensor to your `configuration.yaml`.

The minimum required configuration:

```yaml
binary_sensor:
    - platform: sdnotify
```

## Step 3: Update systemd config

Your systemd config should already exist in a file like `/etc/systemd/system/homeassistant.service`. Add Type,WATCHDOG_USEC,WatchdogSec,Restart=, and RestartSec to your config.

```
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

Lastly, reload systemd
```
sudo systemctl daemon-reload
```

## Step 4: Restart and Test

```
sudo systemctl restart homeassistant.service
```


### Credit

Originally copied from https://gist.github.com/yottatsa/2395de4ea665fecabf1dfb63796a546b
