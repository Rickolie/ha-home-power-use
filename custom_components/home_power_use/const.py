"""Constants for the Home Power Use (standby power) integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "home_power_use"
VERSION: Final = "0.2.0"

CONF_POWER_SENSOR: Final = "power_sensor"
CONF_ENERGY_PRICE: Final = "energy_price"
CONF_BASELINE_SECONDS: Final = "baseline_seconds"
CONF_OFF_SECONDS: Final = "off_seconds"
CONF_SETTLE_SECONDS: Final = "settle_seconds"

DEFAULT_ENERGY_PRICE: Final = 0.30
DEFAULT_BASELINE_SECONDS: Final = 30
DEFAULT_OFF_SECONDS: Final = 30
DEFAULT_SETTLE_SECONDS: Final = 5
DEFAULT_STANDBY_HOURS: Final = 24.0

DEFAULTS: Final = {
    CONF_ENERGY_PRICE: DEFAULT_ENERGY_PRICE,
    CONF_BASELINE_SECONDS: DEFAULT_BASELINE_SECONDS,
    CONF_OFF_SECONDS: DEFAULT_OFF_SECONDS,
    CONF_SETTLE_SECONDS: DEFAULT_SETTLE_SECONDS,
}

STORAGE_KEY: Final = f"{DOMAIN}.devices"
STORAGE_VERSION: Final = 1

PANEL_URL_PATH: Final = "standby-power"
PANEL_TITLE: Final = "Standby Power"
PANEL_ICON: Final = "mdi:power-plug-off-outline"
PANEL_COMPONENT: Final = "home-power-use-panel"
STATIC_URL: Final = "/home_power_use_frontend"

# Measurement phases
PHASE_IDLE: Final = "idle"
PHASE_BASELINE: Final = "baseline"
PHASE_WAITING_FOR_OFF: Final = "waiting_for_off"
PHASE_SETTLING: Final = "settling"
PHASE_MEASURING_OFF: Final = "measuring_off"
PHASE_DONE: Final = "done"
PHASE_ERROR: Final = "error"

ACTIVE_PHASES: Final = (
    PHASE_BASELINE,
    PHASE_WAITING_FOR_OFF,
    PHASE_SETTLING,
    PHASE_MEASURING_OFF,
)
