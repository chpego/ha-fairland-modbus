"""Binary sensors for the Fairland (Modbus) integration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from fairland_modbus.heat_pump import FairlandHeatPump

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import FairlandConfigEntry
from .entity import FairlandEntity, FairlandEntityDescription

# Coordinator-based, so the platform sends nothing itself.
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class FairlandBinarySensorEntityDescription(
    BinarySensorEntityDescription, FairlandEntityDescription
):
    """Describe a Fairland binary sensor."""

    value_fn: Callable[[FairlandHeatPump], bool | None]


BINARY_SENSORS: tuple[FairlandBinarySensorEntityDescription, ...] = (
    FairlandBinarySensorEntityDescription(
        key="malfunction",
        translation_key="malfunction",
        blocks=("status",),
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda hp: hp.status.malfunction,
    ),
    FairlandBinarySensorEntityDescription(
        key="no_water_flow",
        translation_key="no_water_flow",
        blocks=("status",),
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda hp: hp.status.no_water_flow,
    ),
    # Only seen on a Geco GEPAC08 so far, where it follows the water even
    # while the heat pump is off.
    FairlandBinarySensorEntityDescription(
        key="water_flow",
        translation_key="water_flow",
        blocks=("status",),
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda hp: hp.status.flow_switch_closed,
    ),
    FairlandBinarySensorEntityDescription(
        key="compressor",
        translation_key="compressor",
        blocks=("status",),
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda hp: hp.status.compressor_demand,
    ),
    FairlandBinarySensorEntityDescription(
        key="remote_switch",
        translation_key="remote_switch",
        blocks=("status",),
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda hp: hp.status.remote_switch_closed,
    ),
    FairlandBinarySensorEntityDescription(
        key="defrosting",
        translation_key="defrosting",
        blocks=("status",),
        value_fn=lambda hp: hp.status.defrosting,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FairlandConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Fairland binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        FairlandBinarySensor(coordinator, description) for description in BINARY_SENSORS
    )


class FairlandBinarySensor(FairlandEntity, BinarySensorEntity):
    """A Fairland binary sensor."""

    entity_description: FairlandBinarySensorEntityDescription

    @property
    @override
    def is_on(self) -> bool | None:
        """The state the heat pump reports."""
        return self.entity_description.value_fn(self.coordinator.heat_pump)
