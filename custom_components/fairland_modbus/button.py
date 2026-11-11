"""Buttons for the Fairland (Modbus) integration."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import FairlandConfigEntry
from .entity import FairlandEntity, FairlandEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class FairlandButtonEntityDescription(
    ButtonEntityDescription, FairlandEntityDescription
):
    """Describe a Fairland button."""


START_DEFROST = FairlandButtonEntityDescription(
    key="start_defrost",
    translation_key="start_defrost",
    blocks=("controls",),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FairlandConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Fairland buttons."""
    async_add_entities([FairlandDefrostButton(entry.runtime_data, START_DEFROST)])


class FairlandDefrostButton(FairlandEntity, ButtonEntity):
    """Ask the heat pump to defrost now."""

    entity_description: FairlandButtonEntityDescription

    @override
    async def async_press(self) -> None:
        """Start a defrost."""
        await self._async_write(self.coordinator.heat_pump.async_start_defrost())
