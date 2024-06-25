# homeassistant-aerogarden

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

[![Aerogarden API Status](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml)

[![codecov](https://codecov.io/gh/dalinicus/homeassistant-aerogarden/graph/badge.svg?token=TNP1DC74AW)](https://codecov.io/gh/dalinicus/homeassistant-aerogarden)
[![Tests](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/tests.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/tests.yaml)

[![Code Style](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/style.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/style.yaml)
[![HACS/HASS](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/validate.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/validate.yaml)
[![CodeQL](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/codeql.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/codeql.yaml)

This is a custom component for [Home Assistant](http://home-assistant.io) that adds support for the Miracle Grow [AeroGarden](http://www.aerogarden.com) Wi-fi hydroponic gardens.

## Background

Overhaul of work done by [jacobdonenfeld](https://github.com/jacobdonenfeld/homeassistant-aerogarden) who picked up the torch from [ksheumaker](https://github.com/ksheumaker/homeassistant-aerogarden) who was inspired by a [forum post by epotex](https://community.home-assistant.io/t/first-timer-trying-to-convert-a-working-script-to-create-support-for-a-new-platform).  Utilizes the non-public Aerogarden API to read and write information for gardens added to a user's Aerogarden account.

## Data available

A device will be created for each Aerogarden registered in a user's Aerogarden account.  A device has the following sensors associated with it:

### Binary Sensors

* Light - `On` if garden light is on; `Off` otherwise
* Needs Nutrients - `Problem` if garden needs nutrients; `OK` otherwise
* Needs Water -  `Problem` if garden needs water; `OK` otherwise
* Pump - `Running` if garden pump is running; `Not running` otherwise

### Sensors

* Nutrient Days - Days left in the configured nutrient cycle.
* Planted Days - Days since the garden was initially planted.
* Water Level - Current state of the reservoir level; `Full`, `Medium`, or `Low`

![Aerogarden-Device](/images/aerogarden-device.png)

## Tested Models

* Harvest Wi-fi
* Bounty

Other models are expected to work. Actively interested in users with a multi-garden setup to test code paths I cannot with my single-garden setup.

## Installation

### HACS


This integration is made available through the default HACS feed.  Simply search for and install the integration from the HACS interface as normal.  

![HACS-Instal](/images/hacs-install.png)

Please see the [official HACS documentation](https://hacs.xyz) for information on how to install and use HACS.


### Manual Installation

Copy `custom_components/aerogarden` into your Home Assistant `$HA_HOME/config` directory, then restart Home Assistant

## Initial Setup

Add an integration entry as normal from integration section of the home assistant settings.  You'll need the following configuration items

* **Email**: The e-mail registered with your Aerogarden account.
* **Password**: The password for this account.

![Initial-Setup](/images/initial-setup.png)

## Additional Configuration

After adding an integration entry, the following additional configurations can be modified via the configuration options dialog.

* **Polling Interval (Seconds)**: The time between update calls to the Aerogarden API.  Minimum allowed polling interval is 30 seconds.
* **Update Password**: When provided, updates the password used to connect to your Aerogarden account.  Requires Home Assistant restart.

![Additional-Configuration](/images/additional-configuration.png)

## Note about the Aerogarden API

This integration uses a non-public API to fetch information; the same API that is used by Aerogarden devices.  This API has had a number of outages this last year, which leads to issues using this integration.  Please make sure this status badge is reporting green before opening any issues, as a red status would indicate problems with the API and not the Integration

[![Aerogarden API Status](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml)
