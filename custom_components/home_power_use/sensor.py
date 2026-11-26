"""Summary sensors for the standby power database."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HomePowerUseConfigEntry
from .const import DOMAIN, VERSION
from .manager import StandbyPowerManager


@dataclass(frozen=True, kw_only=True)
class StandbySensorDescription(SensorEntityDescription):
    """Describes a standby summary sensor."""

    value_fn: Callable[[dict[str, Any]], float]
    devices_attr: Callable[[dict[str, Any]], bool] | None = None


SENSORS: tuple[StandbySensorDescription, ...] = (
    StandbySensorDescription(
        key="total_standby_power",
        translation_key="total_standby_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda t: t["total_standby_power"],
        devices_attr=lambda d: True,
    ),
    StandbySensorDescription(
        key="avoidable_standby_power",
        translation_key="avoidable_standby_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda t: t["avoidable_standby_power"],
        devices_attr=lambda d: d["can_switch_off"],
    ),
    StandbySensorDescription(
        key="yearly_energy_savings",
        translation_key="yearly_energy_savings",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
        value_fn=lambda t: t["yearly_kwh_saved"],
    ),
    StandbySensorDescription(
        key="yearly_cost_savings",
        translation_key="yearly_cost_savings",
        device_class=SensorDeviceClass.MONETARY,
        suggested_display_precision=2,
        value_fn=lambda t: t["yearly_cost_saved"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomePowerUseConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the summary sensors."""
    manager = entry.runtime_data
    async_add_entities(StandbySensor(manager, entry.entry_id, d) for d in SENSORS)


class StandbySensor(SensorEntity):
    """A sensor summarising the standby power database."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: StandbySensorDescription

    def __init__(
        self,
        manager: StandbyPowerManager,
        entry_id: str,
        description: StandbySensorDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._manager = manager
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Standby Power",
            entry_type=DeviceEntryType.SERVICE,
            sw_version=VERSION,
        )
        if description.device_class == SensorDeviceClass.MONETARY:
            self._attr_native_unit_of_measurement = manager.hass.config.currency

    async def async_added_to_hass(self) -> None:
        """Listen for database changes."""
        self.async_on_remove(
            self._manager.async_add_listener(self._handle_update, devices_only=True)
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        """Return the state."""
        return self.entity_description.value_fn(self._manager.totals)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """List the devices that make up the value."""
        if (selector := self.entity_description.devices_attr) is None:
            return None
        return {
            "devices": {
                d["name"]: d["standby_power"]
                for d in self._manager.devices.values()
                if selector(d)
            }
        }
