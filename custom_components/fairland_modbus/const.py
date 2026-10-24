"""Constants for the Fairland (Modbus) integration."""

from datetime import timedelta

DOMAIN = "fairland_modbus"
MANUFACTURER = "Fairland"

CONF_UNIT_ID = "unit_id"

TYPE_SERIAL = "serial"
TYPE_TCP = "tcp"

DEFAULT_PORT = 502

UPDATE_INTERVAL = timedelta(seconds=30)
