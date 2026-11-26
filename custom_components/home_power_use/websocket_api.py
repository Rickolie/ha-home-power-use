"""Websocket commands used by the side panel."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .manager import StandbyPowerManager


@callback
def async_register_websocket_commands(hass: HomeAssistant) -> None:
    """Register the websocket commands."""
    for command in (
        ws_subscribe,
        ws_start_measurement,
        ws_device_off,
        ws_cancel_measurement,
        ws_add_device,
        ws_update_device,
        ws_delete_device,
    ):
        websocket_api.async_register_command(hass, command)


def _manager(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> StandbyPowerManager | None:
    manager: StandbyPowerManager | None = hass.data.get(DOMAIN)
    if manager is None:
        connection.send_error(
            msg["id"], "not_loaded", "The Home Power Use integration is not loaded"
        )
    return manager


def _run(
    connection: websocket_api.ActiveConnection, msg: dict, func: Any, *args: Any, **kwargs: Any
) -> None:
    try:
        result = func(*args, **kwargs)
    except HomeAssistantError as err:
        connection.send_error(msg["id"], "failed", str(err))
        return
    connection.send_result(msg["id"], result if isinstance(result, dict) else None)


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/subscribe"})
@callback
def ws_subscribe(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Subscribe to devices and measurement updates."""
    if (manager := _manager(hass, connection, msg)) is None:
        return

    @callback
    def forward() -> None:
        connection.send_message(
            websocket_api.event_message(msg["id"], manager.as_dict())
        )

    connection.subscriptions[msg["id"]] = manager.async_add_listener(forward)
    connection.send_result(msg["id"])
    forward()


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/measurement/start",
        vol.Optional("name"): vol.All(str, vol.Strip, vol.Length(min=1, max=100)),
        vol.Optional("device_id"): str,
    }
)
@callback
def ws_start_measurement(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Start a standby measurement for a new or existing device."""
    if (manager := _manager(hass, connection, msg)) is None:
        return
    _run(
        connection,
        msg,
        manager.async_start_measurement,
        name=msg.get("name"),
        device_id=msg.get("device_id"),
    )


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/measurement/device_off"})
@callback
def ws_device_off(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Confirm the device has been unplugged / turned off."""
    if (manager := _manager(hass, connection, msg)) is None:
        return
    _run(connection, msg, manager.async_device_off)


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/measurement/cancel"})
@callback
def ws_cancel_measurement(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Cancel a running measurement or dismiss its result."""
    if (manager := _manager(hass, connection, msg)) is None:
        return
    _run(connection, msg, manager.async_cancel_measurement)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/device/add",
        vol.Required("name"): vol.All(str, vol.Strip, vol.Length(min=1, max=100)),
        vol.Optional("standby_power", default=0.0): vol.All(
            vol.Coerce(float), vol.Range(min=0)
        ),
    }
)
@callback
def ws_add_device(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Add a device with a manually entered standby power."""
    if (manager := _manager(hass, connection, msg)) is None:
        return
    _run(
        connection,
        msg,
        manager.async_add_device,
        msg["name"],
        msg["standby_power"],
    )


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/device/update",
        vol.Required("device_id"): str,
        vol.Optional("name"): vol.All(str, vol.Strip, vol.Length(min=1, max=100)),
        vol.Optional("standby_power"): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Optional("can_switch_off"): bool,
        vol.Optional("standby_hours"): vol.All(
            vol.Coerce(float), vol.Range(min=0, max=24)
        ),
    }
)
@callback
def ws_update_device(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Update a device."""
    if (manager := _manager(hass, connection, msg)) is None:
        return
    changes = {
        key: msg[key]
        for key in ("name", "standby_power", "can_switch_off", "standby_hours")
        if key in msg
    }
    _run(connection, msg, manager.async_update_device, msg["device_id"], **changes)


@websocket_api.require_admin
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/device/delete",
        vol.Required("device_id"): str,
    }
)
@callback
def ws_delete_device(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Delete a device."""
    if (manager := _manager(hass, connection, msg)) is None:
        return
    _run(connection, msg, manager.async_delete_device, msg["device_id"])
