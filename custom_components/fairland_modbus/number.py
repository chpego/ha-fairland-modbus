"""Numbers for the Fairland (Modbus) integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from fairland_modbus.heat_pump import FairlandHeatPump

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import FairlandConfigEntry
from .entity import FairlandEntity, FairlandEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class FairlandNumberEntityDescription(
    NumberEntityDescription, FairlandEntityDescription
):
    """Describe one of the board's service parameters.

    The key is the parameter's name in the library. They are installer
    settings, so they are disabled by default.
    """

    value_fn: Callable[[FairlandHeatPump], float | None]
    blocks: tuple[str, ...] = ("settings",)
    entity_category: EntityCategory | None = EntityCategory.CONFIG
    entity_registry_enabled_default: bool = False
    mode: NumberMode = NumberMode.BOX


def _minutes(
    key: str,
    low: int,
    high: int,
    step: int,
    value_fn: Callable[[FairlandHeatPump], float | None],
) -> FairlandNumberEntityDescription:
    return FairlandNumberEntityDescription(
        key=key,
        translation_key=key,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_min_value=low,
        native_max_value=high,
        native_step=step,
        value_fn=value_fn,
    )


def _degrees(
    key: str, low: int, high: int, value_fn: Callable[[FairlandHeatPump], float | None]
) -> FairlandNumberEntityDescription:
    return FairlandNumberEntityDescription(
        key=key,
        translation_key=key,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=low,
        native_max_value=high,
        native_step=1,
        value_fn=value_fn,
    )


# The ranges and steps of the register table, parameters P1 to P5.
NUMBERS: tuple[FairlandNumberEntityDescription, ...] = (
    _minutes("pump_run_time", 10, 120, 5, lambda hp: hp.settings.pump_run_time),
    _minutes("defrost_interval", 30, 90, 1, lambda hp: hp.settings.defrost_interval),
    _degrees(
        "defrost_start_temperature",
        -17,
        0,
        lambda hp: hp.settings.defrost_start_temperature,
    ),
    _minutes(
        "defrost_max_duration", 1, 12, 1, lambda hp: hp.settings.defrost_max_duration
    ),
    _degrees(
        "defrost_end_temperature", 8, 30, lambda hp: hp.settings.defrost_end_temperature
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FairlandConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Fairland numbers."""
    coordinator = entry.runtime_data
    async_add_entities(
        FairlandNumber(coordinator, description) for description in NUMBERS
    )


class FairlandNumber(FairlandEntity, NumberEntity):
    """A service parameter of the board."""

    entity_description: FairlandNumberEntityDescription

    @property
    @override
    def native_value(self) -> float | None:
        """The value the board is set to."""
        return self.entity_description.value_fn(self.coordinator.heat_pump)

    @override
    async def async_set_native_value(self, value: float) -> None:
        """Change the parameter."""
        await self._async_write(
            self.coordinator.heat_pump.async_set_setting(
                self.entity_description.key, value
            )
        )
