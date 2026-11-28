# Home Power Use – Standby Power

A Home Assistant custom integration (installable with HACS) that helps you find out
**how much standby power each device in your home uses**, and how much you save by
switching those devices off completely.

It adds a **"Standby Power" side panel** where you:

1. Type a device name and press **Start measurement** (the device is in standby).
2. When asked, **unplug the device or switch it off** at the socket and press **Device is off**.
3. The difference in power before and after is stored in the device database.
4. In the overview, mark which devices **can be switched off** and see how much
   energy (kWh) and money you save per year.

## How it measures

The integration uses one power sensor that measures your whole home (for example a
P1 / DSMR smart meter, HomeWizard, Shelly EM…) or a smart plug.

| Phase | What happens |
| --- | --- |
| Baseline | Power is sampled every second for *Baseline duration* (default 30 s) while the device is in standby. |
| Waiting | You are asked to unplug the device or turn it off completely. |
| Settle | A short wait (default 5 s) so the meter can catch up. |
| Off | Power is sampled again for *Off duration* (default 30 s). |
| Result | `standby power = median(baseline) − median(off)` is written to the database. |

The median is used so that short spikes (a kettle, a fridge compressor starting) have
less influence. The fluctuation of the readings (standard deviation) is stored as well;
if the difference is smaller than that fluctuation, or negative, the result is marked
with a warning so you know to measure again.

**Tips for accurate results**

* Measure when your home is quiet (no washing machine, oven or heat pump starting).
* Use longer durations for small devices (< 2 W) or when your meter only updates every 10 s.
* A smart plug on the device itself gives the most precise result.

## Overview

For every device the panel shows:

* measured standby power (editable, e.g. to correct a noisy measurement)
* **Can be switched off** toggle
* standby hours per day (default 24 h – lower it if the device is actually used part of the day)
* energy and cost per year, and the amount **saved per year** when it is switched off

Devices can also be added manually (without measuring), measured again, renamed or deleted.

## Sensors

The integration also creates sensors you can use on dashboards and in automations:

| Entity | Description |
| --- | --- |
| `sensor.standby_power_total_standby_power` | Sum of the standby power of all devices (W) |
| `sensor.standby_power_avoidable_standby_power` | Sum of devices marked as *can be switched off* (W) |
| `sensor.standby_power_yearly_energy_savings` | Yearly kWh saved by switching those devices off |
| `sensor.standby_power_yearly_cost_savings` | Yearly cost saved (Home Assistant currency) |

## Installation

### HACS (recommended)

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/rickolie/ha-home-power-use`, category **Integration**.
2. Install **Home Power Use - Standby Power** and restart Home Assistant.
3. **Settings → Devices & services → Add integration → Home Power Use - Standby Power**.
4. Choose your power sensor and energy price. The **Standby Power** panel appears in the sidebar (admins only).

### Manual

Copy `custom_components/home_power_use` into your `config/custom_components/` folder and restart.

## Configuration

All settings can be changed later in the **Settings** section at the bottom of the
Standby Power panel (or via **Configure** on the integration). The panel lists all
power sensors with their live value, P1 / smart meter sensors first, so you can
switch to another P1 sensor at any time. Changes apply immediately (no restart) and
existing measurements are kept; settings are locked while a measurement runs.

* **Power sensor** – a sensor with device class `power` in W or kW
* **Energy price per kWh** – used for the cost calculations
* **Baseline / Off measurement duration** – 5–600 s
* **Settle time** – 0–120 s

## Data storage

The device database is stored by Home Assistant in `config/.storage/home_power_use.devices`
and is included in Home Assistant backups.

## Development

```bash
pip install -r requirements_test.txt
pytest
```

The panel (`custom_components/home_power_use/frontend/home-power-use-panel.js`) is a
plain web component without build step. It talks to the backend through these
websocket commands: `home_power_use/subscribe`, `measurement/start`,
`measurement/device_off`, `measurement/cancel`, `device/add`, `device/update`, `device/delete`, `settings/update`.
