# homeassistant-aerogarden
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Aerogarden API Status](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml)


[![codecov](https://codecov.io/gh/dalinicus/homeassistant-aerogarden/graph/badge.svg?token=TNP1DC74AW)](https://codecov.io/gh/dalinicus/homeassistant-aerogarden)
[![Tests](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/tests.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/tests.yaml)

[![Code Style](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/style.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/style.yaml)
[![HACS/HASS](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/validate.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/validate.yaml)
[![CodeQL](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/codeql.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/codeql.yaml)

This is a custom component for [Home Assistant](http://home-assistant.io) that adds support for the Miracle Grow [AeroGarden](http://www.aerogarden.com) Wifi hydroponic gardens.

## Background
Overhaul of work done by [jacobdonenfeld](https://github.com/jacobdonenfeld/homeassistant-aerogarden) who picked up the torch from [ksheumaker](https://github.com/ksheumaker/homeassistant-aerogarden) who was inspired by a [forum post by epotex](https://community.home-assistant.io/t/first-timer-trying-to-convert-a-working-script-to-create-support-for-a-new-platform).  Utilizes the non-public Aerogarden API to read and write information for gardens added to a user's Aerogarden account.


## Data available
The following sensors will be created for each Aerogarden registered in a user's Aerogarden account.

### Binary Sensors
* Light - `On` if garden light is on; `Off` otherwise
* Needs Nutrients - `Problem` if garden needs nutrients; `OK` otherwise
* Needs Water -  `Problem` if garden needs water; `OK` otherwise
* Pump - `Running` if garden pump is running; `Not running` otherwise

![Binary Sensors](/images/binary-sensors.png)

### Sensors
* Nutrient Days - Days left in the configured nutrient cycle.
* Planted Days - Days since the garden was initially planted.
* Water Level - Current state of the reservoir level; `Full`, `Medium`, or `Low`

![Sensors](/images/sensors.png)

## Tested Models

* Harvest Wifi
* Bounty

Other models are expected to work. Actively interested in users with a multi-garden setup to test code paths I cannot with my single-garden setup.

## Installation

### HACS
Follow [this guide](https://hacs.xyz/docs/faq/custom_repositories/) to add this git repository as a custom HACS repository. Then install from HACS as normal.

### Manual Installation
Copy `custom_components/aerogarden` into your Home Assistant `$HA_HOME/config` directory, then restart Home Assistant

## Note about the Aerogarden API
This integration uses a non-public API to fetch information; the same API that is used by Aerogarden devices.  This API has had a number of outages this last year, which leads to issues using this integration.  Please make sure this status badge is reporting green before opening any issues, as a red status would indicate problems with the API and not the Integration

[![Aerogarden API Status](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml/badge.svg)](https://github.com/dalinicus/homeassistant-aerogarden/actions/workflows/synthetic-api-test.yaml)
