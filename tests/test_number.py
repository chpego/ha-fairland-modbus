"""Tests for the Fairland (Modbus) numbers."""

from modbus_connection.mock import WriteEvent
import pytest
from pytest_homeassistant.common import MockConfigEntry, snapshot_platform
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.number import (
    ATTR_VALUE,
    DOMAIN as NUMBER_DOMAIN,
    SERVICE_SET_VALUE,
)
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from . import FC06

PREFIX = "number.fairland_heat_pump_"


@pytest.fixture
def platforms() -> list[Platform]:
    """Set up only the number platform."""
    return [Platform.NUMBER]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test the service parameters a heat pump gets, and their values."""
    await snapshot_platform(hass, entity_registry, snapshot, init_integration.entry_id)


async def test_disabled_by_default(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test the installer settings all start disabled."""
    entries = er.async_entries_for_config_entry(
        entity_registry, init_integration.entry_id
    )
    assert len(entries) == 5
    assert all(entry.disabled for entry in entries)


@pytest.mark.parametrize(
    ("entity", "value", "register", "raw"),
    [
        pytest.param("pump_sampling_time", 45, 6, 45, id="p1"),
        pytest.param("compressor_run_time_before_defrost", 40, 7, 40, id="p2"),
        # Temperatures are type 1 on the board: raw = (degrees + 30) * 2.
        pytest.param("defrost_start_temperature", -10, 8, 40, id="p3"),
        pytest.param("maximum_defrost_duration", 8, 9, 8, id="p4"),
        pytest.param("defrost_end_temperature", 15, 10, 90, id="p5"),
    ],
)
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "init_integration")
async def test_set_value(
    hass: HomeAssistant,
    writes: list[WriteEvent],
    entity: str,
    value: float,
    register: int,
    raw: int,
) -> None:
    """Test each parameter writes its own holding register."""
    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {ATTR_ENTITY_ID: PREFIX + entity, ATTR_VALUE: value},
        blocking=True,
    )
    assert writes == [WriteEvent("holding", register, [raw], FC06)]


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "init_integration")
async def test_value_off_the_step(
    hass: HomeAssistant, writes: list[WriteEvent]
) -> None:
    """Test a value off the table's step is reported as invalid, not sent."""
    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: PREFIX + "pump_sampling_time", ATTR_VALUE: 42},
            blocking=True,
        )
    assert exc_info.value.translation_key == "invalid_value"
    assert writes == []
