"""Selects for the Fairland (Modbus) integration."""

from dataclasses import dataclass
from typing import override

from fairland_modbus.heat_pump import PumpMode

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import FairlandConfigEntry
from .entity import FairlandEntity, FairlandEntityDescription

PARALLEL_UPDATES = 1

PUMP_MODES = {mode.name.lower(): mode for mode in PumpMode}


@dataclass(frozen=True, kw_only=True)
class FairlandSelectEntityDescription(
    SelectEntityDescription, FairlandEntityDescription
):
    """Describe a Fairland select."""


PUMP_MODE = FairlandSelectEntityDescription(
    key="pump_mode",
    translation_key="pump_mode",
    blocks=("settings",),
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FairlandConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Fairland selects."""
    async_add_entities([FairlandPumpModeSelect(entry.runtime_data, PUMP_MODE)])


class FairlandPumpModeSelect(FairlandEntity, SelectEntity):
    """When the board runs the filtration pump (P0)."""

    entity_description: FairlandSelectEntityDescription
    _attr_options = list(PUMP_MODES)

    @property
    @override
    def current_option(self) -> str | None:
        """The pump mode the board is set to."""
        mode = self.coordinator.heat_pump.settings.pump_mode
        return None if mode is None else mode.name.lower()

    @override
    async def async_select_option(self, option: str) -> None:
        """Change the pump mode."""
        await self._async_write(
            self.coordinator.heat_pump.async_set_pump_mode(PUMP_MODES[option])
        )
