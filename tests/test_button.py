"""Tests for the Fairland (Modbus) button."""

from modbus_connection import IllegalDataValueError, ModbusConnectionError
from modbus_connection.mock import MockModbusUnit, WriteEvent
import pytest
from pytest_homeassistant.common import MockConfigEntry, snapshot_platform
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from . import COIL

START_DEFROST = "button.fairland_heat_pump_start_defrost"


@pytest.fixture
def platforms() -> list[Platform]:
    """Set up only the button platform."""
    return [Platform.BUTTON]


async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test the button a heat pump gets."""
    await snapshot_platform(hass, entity_registry, snapshot, init_integration.entry_id)


@pytest.mark.usefixtures("init_integration")
async def test_start_defrost(hass: HomeAssistant, writes: list[WriteEvent]) -> None:
    """Test the button sets the forced defrost coil, and nothing else."""
    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: START_DEFROST}, blocking=True
    )
    assert writes == [WriteEvent("coil", 1, [True], COIL)]


@pytest.mark.parametrize(
    ("error", "translation_key"),
    [
        pytest.param(IllegalDataValueError(), "write_refused", id="refused"),
        pytest.param(ModbusConnectionError("link down"), "write_failed", id="failed"),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_start_defrost_error(
    hass: HomeAssistant,
    mock_unit: MockModbusUnit,
    error: Exception,
    translation_key: str,
) -> None:
    """Test a write the board refuses, or a link that fails, raises an error."""
    mock_unit.fail_write(1, error, register_type="coil")
    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: START_DEFROST}, blocking=True
        )
    assert exc_info.value.translation_key == translation_key
