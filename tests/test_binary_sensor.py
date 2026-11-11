"""Tests for the Fairland (Modbus) binary sensors."""

from fairland_modbus.heat_pump.testing import HEATING
import pytest
from pytest_homeassistant.common import MockConfigEntry, snapshot_platform
from syrupy.assertion import SnapshotAssertion

from homeassistant.const import STATE_OFF, STATE_ON, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import heating_image

PREFIX = "binary_sensor.fairland_heat_pump_"


@pytest.fixture
def platforms() -> list[Platform]:
    """Set up only the binary sensor platform."""
    return [Platform.BINARY_SENSOR]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test the binary sensors a heat pump gets, and their states."""
    await snapshot_platform(hass, entity_registry, snapshot, init_integration.entry_id)


async def test_enabled_by_default(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test the two contacts start disabled."""
    entries = er.async_entries_for_config_entry(
        entity_registry, init_integration.entry_id
    )
    assert sorted(
        entry.entity_id.removeprefix(PREFIX) for entry in entries if not entry.disabled
    ) == ["compressor", "defrosting", "malfunction", "no_water_flow"]


@pytest.mark.parametrize(
    ("register_image", "key", "state"),
    [
        pytest.param(HEATING, "compressor", STATE_ON, id="compressor_on"),
        pytest.param(
            heating_image(discrete={17: False}),
            "compressor",
            STATE_OFF,
            id="compressor_off",
        ),
        pytest.param(HEATING, "defrosting", STATE_OFF, id="not_defrosting"),
        pytest.param(
            heating_image(discrete={1: True}), "defrosting", STATE_ON, id="defrosting"
        ),
        pytest.param(HEATING, "malfunction", STATE_OFF, id="no_malfunction"),
        pytest.param(
            heating_image(discrete={16: True}),
            "malfunction",
            STATE_ON,
            id="malfunction",
        ),
        pytest.param(HEATING, "no_water_flow", STATE_OFF, id="no_e3"),
        pytest.param(
            heating_image(discrete={51: True}), "no_water_flow", STATE_ON, id="e3"
        ),
        pytest.param(HEATING, "water_flow", STATE_ON, id="water_flows"),
        pytest.param(
            heating_image(discrete={4: False}),
            "water_flow",
            STATE_OFF,
            id="water_stopped",
        ),
        pytest.param(HEATING, "remote_switch", STATE_ON, id="remote_closed"),
        pytest.param(
            heating_image(discrete={3: False}),
            "remote_switch",
            STATE_OFF,
            id="remote_open",
        ),
    ],
    indirect=["register_image"],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "init_integration")
async def test_state(hass: HomeAssistant, key: str, state: str) -> None:
    """Test each binary sensor follows its bit."""
    assert hass.states.get(PREFIX + key).state == state
