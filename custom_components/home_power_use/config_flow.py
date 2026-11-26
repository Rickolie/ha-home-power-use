"""Config flow for Home Power Use."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_BASELINE_SECONDS,
    CONF_ENERGY_PRICE,
    CONF_OFF_SECONDS,
    CONF_POWER_SENSOR,
    CONF_SETTLE_SECONDS,
    DEFAULTS,
    DOMAIN,
    PANEL_TITLE,
)

_SECONDS = NumberSelector(
    NumberSelectorConfig(
        min=5, max=600, step=1, mode=NumberSelectorMode.BOX, unit_of_measurement="s"
    )
)
_SETTLE_SECONDS = NumberSelector(
    NumberSelectorConfig(
        min=0, max=120, step=1, mode=NumberSelectorMode.BOX, unit_of_measurement="s"
    )
)
_PRICE = NumberSelector(
    NumberSelectorConfig(min=0, max=10, step=0.001, mode=NumberSelectorMode.BOX)
)
_POWER_SENSOR = EntitySelector(
    EntitySelectorConfig(domain="sensor", device_class=SensorDeviceClass.POWER)
)


def _schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_POWER_SENSOR, default=values.get(CONF_POWER_SENSOR, vol.UNDEFINED)
            ): _POWER_SENSOR,
            vol.Required(
                CONF_ENERGY_PRICE, default=values[CONF_ENERGY_PRICE]
            ): _PRICE,
            vol.Required(
                CONF_BASELINE_SECONDS, default=values[CONF_BASELINE_SECONDS]
            ): _SECONDS,
            vol.Required(CONF_OFF_SECONDS, default=values[CONF_OFF_SECONDS]): _SECONDS,
            vol.Required(
                CONF_SETTLE_SECONDS, default=values[CONF_SETTLE_SECONDS]
            ): _SETTLE_SECONDS,
        }
    )


def _clean(user_input: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_POWER_SENSOR: user_input[CONF_POWER_SENSOR],
        CONF_ENERGY_PRICE: float(user_input[CONF_ENERGY_PRICE]),
        CONF_BASELINE_SECONDS: int(user_input[CONF_BASELINE_SECONDS]),
        CONF_OFF_SECONDS: int(user_input[CONF_OFF_SECONDS]),
        CONF_SETTLE_SECONDS: int(user_input[CONF_SETTLE_SECONDS]),
    }


class HomePowerUseConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the power sensor used to measure."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if self.hass.states.get(user_input[CONF_POWER_SENSOR]) is None:
                errors[CONF_POWER_SENSOR] = "sensor_not_found"
            else:
                return self.async_create_entry(
                    title=PANEL_TITLE, data={}, options=_clean(user_input)
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema({**DEFAULTS, **(user_input or {})}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return HomePowerUseOptionsFlow()


class HomePowerUseOptionsFlow(OptionsFlow):
    """Change the measuring settings."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if self.hass.states.get(user_input[CONF_POWER_SENSOR]) is None:
                errors[CONF_POWER_SENSOR] = "sensor_not_found"
            else:
                return self.async_create_entry(data=_clean(user_input))

        values = {
            **DEFAULTS,
            **self.config_entry.data,
            **self.config_entry.options,
            **(user_input or {}),
        }
        return self.async_show_form(
            step_id="init", data_schema=_schema(values), errors=errors
        )
