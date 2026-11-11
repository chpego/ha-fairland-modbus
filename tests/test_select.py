"""Tests for the Fairland (Modbus) select."""

from modbus_connection import IllegalDataValueError
from modbus_connection.mock import MockModbusUnit, WriteEvent
import pytest
from pytest_homeassistant.common import MockConfigEntry, snapshot_platform
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.select import (
    ATTR_OPTION,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNKNOWN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from . import FC06, heating_image

PUMP_MODE = "select.fairland_heat_pump_pump_mode"


@pytest.fixture
def platforms() -> list[Platform]:
    """Set up only the select platform."""
    return [Platform.SELECT]


async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test the select a heat pump gets, and its state."""
    await snapshot_platform(hass, entity_registry, snapshot, init_integration.entry_id)


@pytest.mark.parametrize(
    ("register_image", "state"),
    [
        pytest.param(heating_image(holding={5: 0}), "continuous", id="continuous"),
        pytest.param(
            heating_image(holding={5: 1}), "water_temperature", id="water_temperature"
        ),
        pytest.param(
            heating_image(holding={5: 2}),
            "time_and_water_temperature",
            id="time_and_water_temperature",
        ),
        pytest.param(heating_image(holding={5: 7}), STATE_UNKNOWN, id="unknown"),
    ],
    indirect=["register_image"],
)
@pytest.mark.usefixtures("init_integration")
async def test_state(hass: HomeAssistant, state: str) -> None:
    """Test the select shows the pump mode the board is set to (P0)."""
    assert hass.states.get(PUMP_MODE).state == state


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("continuous", 0),
        ("water_temperature", 1),
        ("time_and_water_temperature", 2),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_select_option(
    hass: HomeAssistant, writes: list[WriteEvent], option: str, value: int
) -> None:
    """Test each option writes its value to holding register 5."""
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: PUMP_MODE, ATTR_OPTION: option},
        blocking=True,
    )
    assert writes == [WriteEvent("holding", 5, [value], FC06)]


@pytest.mark.usefixtures("init_integration")
async def test_refused(hass: HomeAssistant, mock_unit: MockModbusUnit) -> None:
    """Test a pump mode the board refuses raises a translated error."""
    mock_unit.fail_write(5, IllegalDataValueError())
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {ATTR_ENTITY_ID: PUMP_MODE, ATTR_OPTION: "water_temperature"},
            blocking=True,
        )
    assert exc_info.value.translation_key == "write_refused"
