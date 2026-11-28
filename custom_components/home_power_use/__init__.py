"""Home Power Use: measure and track the standby power of your devices."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    PANEL_COMPONENT,
    PANEL_ICON,
    PANEL_TITLE,
    PANEL_URL_PATH,
    STATIC_URL,
    VERSION,
)
from .manager import StandbyPowerManager
from .websocket_api import async_register_websocket_commands

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type HomePowerUseConfigEntry = ConfigEntry[StandbyPowerManager]

_STATIC_REGISTERED = f"{DOMAIN}_static_registered"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration (websocket API used by the side panel)."""
    async_register_websocket_commands(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: HomePowerUseConfigEntry) -> bool:
    """Set up Home Power Use from a config entry."""
    manager = StandbyPowerManager(hass, entry)
    await manager.async_load()
    entry.runtime_data = manager
    hass.data[DOMAIN] = manager

    await _async_register_panel(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: HomePowerUseConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        entry.runtime_data.async_shutdown()
        hass.data.pop(DOMAIN, None)
        frontend.async_remove_panel(hass, PANEL_URL_PATH)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: HomePowerUseConfigEntry) -> None:
    """Apply changed options without reloading, so open panels stay connected."""
    entry.runtime_data.async_settings_changed()


async def _async_register_panel(hass: HomeAssistant) -> None:
    """Register the static frontend files and the sidebar panel."""
    if not hass.data.get(_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    STATIC_URL, str(Path(__file__).parent / "frontend"), False
                )
            ]
        )
        hass.data[_STATIC_REGISTERED] = True

    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=PANEL_COMPONENT,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{STATIC_URL}/{PANEL_COMPONENT}.js?v={VERSION}",
        embed_iframe=False,
        require_admin=True,
    )
