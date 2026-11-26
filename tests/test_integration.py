"""Tests for the Home Power Use integration."""

from datetime import timedelta
from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.home_power_use.const import DOMAIN, PANEL_URL_PATH

SENSOR = "sensor.house_power"
OPTIONS = {
    "power_sensor": SENSOR,
    "energy_price": 0.30,
    "baseline_seconds": 5,
    "off_seconds": 5,
    "settle_seconds": 0,
}


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    hass.states.async_set(SENSOR, "250", {"unit_of_measurement": "W"})
    await async_setup_component(hass, "http", {})
    entry = MockConfigEntry(domain=DOMAIN, data={}, options=OPTIONS)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_config_flow(hass: HomeAssistant) -> None:
    """The user can pick a power sensor."""
    hass.states.async_set(SENSOR, "250", {"unit_of_measurement": "W"})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    with patch(
        "custom_components.home_power_use.async_setup_entry", return_value=True
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {**OPTIONS, "baseline_seconds": 30.0}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"]["baseline_seconds"] == 30
    assert result["options"]["power_sensor"] == SENSOR


async def test_measurement_flow(hass: HomeAssistant, hass_ws_client, freezer) -> None:
    """Full measurement via the websocket API, as the panel does it."""
    entry = await _setup(hass)
    assert PANEL_URL_PATH in hass.data["frontend_panels"]
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": f"{DOMAIN}/subscribe"})
    msg = await client.receive_json()
    assert msg["success"]
    sub_id = msg["id"]
    msg = await client.receive_json()
    assert msg["event"]["measurement"]["phase"] == "idle"
    assert msg["event"]["devices"] == []

    await client.send_json_auto_id(
        {"type": f"{DOMAIN}/measurement/start", "name": "TV"}
    )
    # skip event messages until we get the result
    async def result_of(expected_id=None):
        while True:
            m = await client.receive_json()
            if m["type"] == "result":
                return m

    res = await result_of()
    assert res["success"], res

    for _ in range(7):
        freezer.tick(timedelta(seconds=1))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()

    manager = entry.runtime_data
    # time.monotonic is not frozen, so force the phase end
    while manager.measurement["phase"] == "baseline":
        manager._measurement["phase_end"] = 0
        manager._async_tick()
    assert manager.measurement["phase"] == "waiting_for_off"
    assert manager.measurement["baseline_power"] == 250

    # Device unplugged: power drops by 7.5 W
    hass.states.async_set(SENSOR, "0.2425", {"unit_of_measurement": "kW"})
    await client.send_json_auto_id({"type": f"{DOMAIN}/measurement/device_off"})
    res = await result_of()
    assert res["success"], res
    assert manager.measurement["phase"] == "measuring_off"
    for _ in range(3):
        manager._async_tick()
    manager._measurement["phase_end"] = 0
    manager._async_tick()

    m = manager.measurement
    assert m["phase"] == "done"
    assert m["result"]["standby_power"] == 7.5
    devices = list(manager.devices.values())
    assert len(devices) == 1 and devices[0]["name"] == "TV"
    device_id = devices[0]["id"]

    # Mark as switchable, 20 h per day
    await client.send_json_auto_id(
        {
            "type": f"{DOMAIN}/device/update",
            "device_id": device_id,
            "can_switch_off": True,
            "standby_hours": 20,
        }
    )
    res = await result_of()
    assert res["success"], res
    await hass.async_block_till_done()
    totals = manager.totals
    assert totals["avoidable_standby_power"] == 7.5
    assert totals["yearly_kwh_saved"] == round(7.5 * 20 * 365 / 1000, 2)

    state = hass.states.get("sensor.standby_power_avoidable_standby_power")
    assert state is not None and float(state.state) == 7.5
    state = hass.states.get("sensor.standby_power_yearly_cost_savings")
    assert float(state.state) == round(7.5 * 20 * 365 / 1000 * 0.30, 2)

    # Storage persisted
    freezer.tick(timedelta(seconds=5))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    # Manual device and delete
    await client.send_json_auto_id(
        {"type": f"{DOMAIN}/device/add", "name": "Router", "standby_power": 6}
    )
    res = await result_of()
    assert res["success"], res
    assert len(manager.devices) == 2
    await client.send_json_auto_id(
        {"type": f"{DOMAIN}/device/delete", "device_id": device_id}
    )
    res = await result_of()
    assert res["success"], res
    assert len(manager.devices) == 1

    # unload removes panel
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert PANEL_URL_PATH not in hass.data["frontend_panels"]


async def test_negative_difference(hass: HomeAssistant) -> None:
    """Something switching on during the off phase gives 0 W and a warning."""
    entry = await _setup(hass)
    manager = entry.runtime_data
    manager.async_start_measurement("Lamp")
    manager._async_tick()
    manager._measurement["phase_end"] = 0
    manager._async_tick()
    manager.async_device_off()
    hass.states.async_set(SENSOR, "900", {"unit_of_measurement": "W"})
    manager._async_tick()
    manager._measurement["phase_end"] = 0
    manager._async_tick()
    assert manager.measurement["phase"] == "done"
    assert manager.measurement["result"]["warning"] == "negative"
    assert manager.measurement["result"]["standby_power"] == 0
    await hass.config_entries.async_unload(entry.entry_id)


async def test_unavailable_sensor(hass: HomeAssistant) -> None:
    """Starting fails when the sensor is unavailable."""
    entry = await _setup(hass)
    hass.states.async_set(SENSOR, "unavailable")
    manager = entry.runtime_data
    from homeassistant.exceptions import HomeAssistantError
    import pytest

    with pytest.raises(HomeAssistantError):
        manager.async_start_measurement("X")
    await hass.config_entries.async_unload(entry.entry_id)
