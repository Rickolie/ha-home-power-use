"""Device storage and the standby measurement state machine."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from statistics import median, pstdev
import time
from typing import Any
import uuid

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    ACTIVE_PHASES,
    CONF_BASELINE_SECONDS,
    CONF_ENERGY_PRICE,
    CONF_OFF_SECONDS,
    CONF_POWER_SENSOR,
    CONF_SETTLE_SECONDS,
    DEFAULT_STANDBY_HOURS,
    DEFAULTS,
    PHASE_BASELINE,
    PHASE_DONE,
    PHASE_ERROR,
    PHASE_IDLE,
    PHASE_MEASURING_OFF,
    PHASE_SETTLING,
    PHASE_WAITING_FOR_OFF,
    STORAGE_KEY,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

TICK_INTERVAL = timedelta(seconds=1)

_UNIT_FACTORS = {"W": 1.0, "kW": 1000.0, "MW": 1_000_000.0, "mW": 0.001}


def _yearly_kwh(device: dict[str, Any]) -> float:
    """Return the yearly standby energy of a device in kWh."""
    return device["standby_power"] * device["standby_hours"] * 365 / 1000


class StandbyPowerManager:
    """Keeps the device database and runs standby measurements."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the manager."""
        self.hass = hass
        self.entry = entry
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, STORAGE_KEY
        )
        self.devices: dict[str, dict[str, Any]] = {}
        self._listeners: list[Callable[[], None]] = []
        self._device_listeners: list[Callable[[], None]] = []
        self._unsub_tick: CALLBACK_TYPE | None = None
        self._measurement: dict[str, Any] = {}
        self._reset_measurement()

    # ------------------------------------------------------------------ setup

    async def async_load(self) -> None:
        """Load the device database from storage."""
        data = await self._store.async_load() or {}
        for raw in data.get("devices", []):
            device = {
                "id": raw["id"],
                "name": raw.get("name", "?"),
                "standby_power": float(raw.get("standby_power", 0.0)),
                "can_switch_off": bool(raw.get("can_switch_off", False)),
                "standby_hours": float(
                    raw.get("standby_hours", DEFAULT_STANDBY_HOURS)
                ),
                "baseline_power": raw.get("baseline_power"),
                "off_power": raw.get("off_power"),
                "noise": raw.get("noise"),
                "warning": raw.get("warning"),
                "measured_at": raw.get("measured_at"),
                "created_at": raw.get("created_at"),
            }
            self.devices[device["id"]] = device

    @callback
    def async_shutdown(self) -> None:
        """Stop any running measurement."""
        self._stop_tick()
        self._listeners.clear()
        self._device_listeners.clear()

    @callback
    def _schedule_save(self) -> None:
        self._store.async_delay_save(
            lambda: {"devices": list(self.devices.values())}, 1
        )

    # -------------------------------------------------------------- listeners

    @callback
    def async_add_listener(
        self, update_callback: Callable[[], None], devices_only: bool = False
    ) -> CALLBACK_TYPE:
        """Listen for changes. Returns a function that removes the listener."""
        target = self._device_listeners if devices_only else self._listeners
        target.append(update_callback)

        @callback
        def remove() -> None:
            if update_callback in target:
                target.remove(update_callback)

        return remove

    @callback
    def _notify(self, devices_changed: bool = False) -> None:
        for listener in list(self._listeners):
            listener()
        if devices_changed:
            for listener in list(self._device_listeners):
                listener()

    # --------------------------------------------------------------- settings

    @property
    def settings(self) -> dict[str, Any]:
        """Return the merged settings of the config entry."""
        return {**DEFAULTS, **self.entry.data, **self.entry.options}

    @property
    def power_sensor(self) -> str:
        """Return the entity id of the power sensor used for measuring."""
        return self.settings[CONF_POWER_SENSOR]

    @property
    def energy_price(self) -> float:
        """Return the energy price per kWh."""
        return float(self.settings[CONF_ENERGY_PRICE])

    def read_power(self) -> float | None:
        """Return the current power of the measuring sensor in W."""
        state = self.hass.states.get(self.power_sensor)
        if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return None
        try:
            value = float(state.state)
        except ValueError:
            return None
        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT, "W")
        return value * _UNIT_FACTORS.get(unit, 1.0)

    # ----------------------------------------------------------------- devices

    def device_as_dict(self, device: dict[str, Any]) -> dict[str, Any]:
        """Return a device including calculated values."""
        yearly_kwh = _yearly_kwh(device)
        return {
            **device,
            "yearly_kwh": round(yearly_kwh, 2),
            "yearly_cost": round(yearly_kwh * self.energy_price, 2),
        }

    @property
    def totals(self) -> dict[str, Any]:
        """Return summed values over all devices."""
        devices = list(self.devices.values())
        switchable = [d for d in devices if d["can_switch_off"]]
        total_kwh = sum(_yearly_kwh(d) for d in devices)
        saved_kwh = sum(_yearly_kwh(d) for d in switchable)
        return {
            "device_count": len(devices),
            "switchable_count": len(switchable),
            "total_standby_power": round(sum(d["standby_power"] for d in devices), 1),
            "avoidable_standby_power": round(
                sum(d["standby_power"] for d in switchable), 1
            ),
            "yearly_kwh_total": round(total_kwh, 2),
            "yearly_cost_total": round(total_kwh * self.energy_price, 2),
            "yearly_kwh_saved": round(saved_kwh, 2),
            "yearly_cost_saved": round(saved_kwh * self.energy_price, 2),
        }

    @callback
    def async_add_device(
        self,
        name: str,
        standby_power: float = 0.0,
        **extra: Any,
    ) -> dict[str, Any]:
        """Add a device to the database."""
        now = dt_util.utcnow().isoformat()
        device = {
            "id": uuid.uuid4().hex,
            "name": name,
            "standby_power": round(float(standby_power), 1),
            "can_switch_off": False,
            "standby_hours": DEFAULT_STANDBY_HOURS,
            "baseline_power": None,
            "off_power": None,
            "noise": None,
            "warning": None,
            "measured_at": None,
            "created_at": now,
        }
        device.update(extra)
        self.devices[device["id"]] = device
        self._schedule_save()
        self._notify(devices_changed=True)
        return device

    @callback
    def async_update_device(self, device_id: str, **changes: Any) -> dict[str, Any]:
        """Update fields of a device."""
        device = self._get_device(device_id)
        allowed = {"name", "standby_power", "can_switch_off", "standby_hours"}
        for key, value in changes.items():
            if key in allowed and value is not None:
                device[key] = value
        if "standby_power" in changes and changes["standby_power"] is not None:
            # A manual value replaces the measurement details.
            device["standby_power"] = round(float(changes["standby_power"]), 1)
            device["warning"] = None
        self._schedule_save()
        self._notify(devices_changed=True)
        return device

    @callback
    def async_delete_device(self, device_id: str) -> None:
        """Delete a device."""
        self._get_device(device_id)
        del self.devices[device_id]
        if self._measurement["device_id"] == device_id and (
            self._measurement["phase"] in ACTIVE_PHASES
        ):
            self.async_cancel_measurement()
        self._schedule_save()
        self._notify(devices_changed=True)

    def _get_device(self, device_id: str) -> dict[str, Any]:
        try:
            return self.devices[device_id]
        except KeyError as err:
            raise HomeAssistantError(f"Unknown device {device_id}") from err

    # ------------------------------------------------------------ measurement

    def _reset_measurement(self) -> None:
        self._measurement = {
            "phase": PHASE_IDLE,
            "name": None,
            "device_id": None,
            "phase_end": None,
            "phase_duration": None,
            "baseline_samples": [],
            "off_samples": [],
            "result": None,
            "error": None,
        }

    @property
    def measurement(self) -> dict[str, Any]:
        """Return the public state of the current measurement."""
        m = self._measurement
        remaining = None
        if m["phase_end"] is not None:
            remaining = max(0, round(m["phase_end"] - time.monotonic()))
        base = m["baseline_samples"]
        off = m["off_samples"]
        return {
            "phase": m["phase"],
            "name": m["name"],
            "device_id": m["device_id"],
            "remaining": remaining,
            "duration": m["phase_duration"],
            "baseline_power": round(median(base), 1) if base else None,
            "baseline_samples": len(base),
            "off_power": round(median(off), 1) if off else None,
            "off_samples": len(off),
            "result": m["result"],
            "error": m["error"],
        }

    def as_dict(self) -> dict[str, Any]:
        """Return the complete state for the frontend panel."""
        settings = self.settings
        return {
            "devices": [
                self.device_as_dict(d)
                for d in sorted(
                    self.devices.values(), key=lambda d: d["name"].lower()
                )
            ],
            "totals": self.totals,
            "measurement": self.measurement,
            "settings": {
                "power_sensor": self.power_sensor,
                "energy_price": self.energy_price,
                "currency": self.hass.config.currency,
                "baseline_seconds": int(settings[CONF_BASELINE_SECONDS]),
                "off_seconds": int(settings[CONF_OFF_SECONDS]),
                "settle_seconds": int(settings[CONF_SETTLE_SECONDS]),
                "entry_id": self.entry.entry_id,
            },
        }

    @callback
    def async_start_measurement(
        self, name: str | None = None, device_id: str | None = None
    ) -> None:
        """Start measuring: first the baseline with the device in standby."""
        if self._measurement["phase"] in ACTIVE_PHASES:
            raise HomeAssistantError("A measurement is already running")
        if device_id is not None:
            name = self._get_device(device_id)["name"]
        if not name:
            raise HomeAssistantError("A device name is required")
        if self.read_power() is None:
            raise HomeAssistantError(
                f"Power sensor {self.power_sensor} is unavailable"
            )

        self._reset_measurement()
        self._measurement["name"] = name
        self._measurement["device_id"] = device_id
        self._set_phase(PHASE_BASELINE, self.settings[CONF_BASELINE_SECONDS])
        self._start_tick()
        self._notify()

    @callback
    def async_device_off(self) -> None:
        """Called by the user once the device has been unplugged / turned off."""
        if self._measurement["phase"] != PHASE_WAITING_FOR_OFF:
            raise HomeAssistantError("The measurement is not waiting for the device")
        settle = int(self.settings[CONF_SETTLE_SECONDS])
        if settle > 0:
            self._set_phase(PHASE_SETTLING, settle)
        else:
            self._set_phase(PHASE_MEASURING_OFF, self.settings[CONF_OFF_SECONDS])
        self._start_tick()
        self._notify()

    @callback
    def async_cancel_measurement(self) -> None:
        """Cancel the running measurement, or dismiss a finished one."""
        self._stop_tick()
        self._reset_measurement()
        self._notify()

    def _set_phase(self, phase: str, duration: float | None = None) -> None:
        self._measurement["phase"] = phase
        if duration is None:
            self._measurement["phase_end"] = None
            self._measurement["phase_duration"] = None
        else:
            self._measurement["phase_end"] = time.monotonic() + float(duration)
            self._measurement["phase_duration"] = int(duration)

    def _start_tick(self) -> None:
        if self._unsub_tick is None:
            self._unsub_tick = async_track_time_interval(
                self.hass, self._async_tick, TICK_INTERVAL
            )

    def _stop_tick(self) -> None:
        if self._unsub_tick is not None:
            self._unsub_tick()
            self._unsub_tick = None

    def _fail(self, error: str) -> None:
        self._stop_tick()
        self._set_phase(PHASE_ERROR)
        self._measurement["error"] = error

    @callback
    def _async_tick(self, _now: Any = None) -> None:
        """Take a sample every second and advance the phases."""
        m = self._measurement
        phase = m["phase"]
        now = time.monotonic()
        power = self.read_power()
        ended = m["phase_end"] is not None and now >= m["phase_end"]

        if phase == PHASE_BASELINE:
            if power is not None:
                m["baseline_samples"].append(power)
            if ended:
                if not m["baseline_samples"]:
                    self._fail("no_samples")
                else:
                    self._stop_tick()
                    self._set_phase(PHASE_WAITING_FOR_OFF)
        elif phase == PHASE_SETTLING:
            if ended:
                self._set_phase(PHASE_MEASURING_OFF, self.settings[CONF_OFF_SECONDS])
        elif phase == PHASE_MEASURING_OFF:
            if power is not None:
                m["off_samples"].append(power)
            if ended:
                if not m["off_samples"]:
                    self._fail("no_samples")
                else:
                    self._finish()
                    return
        else:
            self._stop_tick()
            return
        self._notify()

    def _finish(self) -> None:
        """Calculate the standby power and write it to the database."""
        self._stop_tick()
        m = self._measurement
        base_samples = m["baseline_samples"]
        off_samples = m["off_samples"]
        baseline = median(base_samples)
        off = median(off_samples)
        noise = max(
            pstdev(base_samples) if len(base_samples) > 1 else 0.0,
            pstdev(off_samples) if len(off_samples) > 1 else 0.0,
        )
        diff = baseline - off
        warning = None
        if diff < 0:
            warning = "negative"
            diff = 0.0
        elif diff < noise:
            warning = "noisy"

        values = {
            "standby_power": round(diff, 1),
            "baseline_power": round(baseline, 1),
            "off_power": round(off, 1),
            "noise": round(noise, 1),
            "warning": warning,
            "measured_at": dt_util.utcnow().isoformat(),
        }
        if m["device_id"] in self.devices:
            device = self.devices[m["device_id"]]
            device.update(values)
            self._schedule_save()
        else:
            device = self.async_add_device(m["name"], **values)
            m["device_id"] = device["id"]

        _LOGGER.debug(
            "Standby measurement for %s: %.1f W (baseline %.1f W, off %.1f W)",
            device["name"],
            diff,
            baseline,
            off,
        )
        m["result"] = {"device_id": device["id"], **values}
        self._set_phase(PHASE_DONE)
        self._notify(devices_changed=True)
