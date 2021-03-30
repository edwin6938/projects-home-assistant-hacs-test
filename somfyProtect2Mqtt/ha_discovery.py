from somfy_protect_api.api.model import Site, Device
from somfy_protect_api.api.devices.category import Category

DEVICE_CAPABILITIES = {
    "temperature": {
        "type": "sensor",
        "config": {"device_class": "temperature", "unit_of_measurement": "°C",},
    },
    "battery_level": {
        "type": "sensor",
        "config": {"device_class": "battery", "unit_of_measurement": "%",},
    },
    "battery_low": {"type": "binary_sensor", "config": {"device_class": "battery",},},
    "rlink_quality": {
        "type": "sensor",
        "config": {"device_class": "signal_strength", "unit_of_measurement": "dB",},
    },
    "rlink_quality_percent": {
        "type": "sensor",
        "config": {"device_class": "signal_strength", "unit_of_measurement": "%",},
    },
    "wifi_level": {
        "type": "sensor",
        "config": {"device_class": "signal_strength", "unit_of_measurement": "dB",},
    },
    "wifi_level_percent": {
        "type": "sensor",
        "config": {"device_class": "signal_strength", "unit_of_measurement": "%",},
    },
    "recalibration_required": {
        "type": "binary_sensor",
        "config": {"device_class": "problem",},
    },
    "cover_present": {
        "type": "binary_sensor",
        "config": {"pl_on": "True", "pl_off": "False",},
    },
    "shutter_state": {
        "type": "switch",
        "config": {"pl_on": "opened", "pl_off": "closed",},
    },
}


def ha_discovery_alarm(site: Site, mqtt_config: dict):
    site_config = {}

    site_info = {
        "identifiers": [site.id],
        "manufacturer": "Somfy",
        "model": "Somfy Home Alarm",
        "name": site.label,
        "sw_version": "SomfyProtect2MQTT: Alpha",
    }

    command_topic = (
        f"{mqtt_config.get('topic_prefix', 'somfyProtect2mqtt')}/{site.id}/command"
    )
    site_config[
        "topic"
    ] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/alarm_control_panel/{site.id}/alarm/config"
    site_config["config"] = {
        "name": site.label,
        "unique_id": f"{site.id}_{site.label}",
        "state_topic": f"{mqtt_config.get('topic_prefix', 'somfyProtect2mqtt')}/{site.id}/state",
        "command_topic": command_topic,
        "payload_arm_away": "armed",
        "payload_arm_night": "partial",
        "payload_disarm": "disarmed",
        "value_template": "{{ value_json.security_level }}",
        "device": site_info,
    }

    return site_config


def ha_discovery_devices(
    site_id: str, device: Device, mqtt_config: dict, sensor_name: str,
):
    device_config = {}
    device_type = DEVICE_CAPABILITIES.get(sensor_name).get("type")

    device_info = {
        "identifiers": [device.id],
        "manufacturer": "Somfy",
        "model": device.device_definition.get("label"),
        "name": device.label,
        "sw_version": device.version,
    }

    command_topic = f"{mqtt_config.get('topic_prefix', 'somfyProtect2mqtt')}/{site_id}/{device.id}/command"
    device_config[
        "topic"
    ] = f"{mqtt_config.get('ha_discover_prefix', 'homeassistant')}/{device_type}/{site_id}_{device.id}/{sensor_name}/config"
    device_config["config"] = {
        "name": f"{device.label} {sensor_name}",
        "unique_id": f"{device.id}_{sensor_name}",
        "state_topic": f"{mqtt_config.get('topic_prefix', 'somfyProtect2mqtt')}/{site_id}/{device.id}/state",
        "value_template": "{{ value_json." + sensor_name + " }}",
        "device": device_info,
    }

    for config_entry in DEVICE_CAPABILITIES.get(sensor_name).get("config"):
        device_config["config"][config_entry] = (
            DEVICE_CAPABILITIES.get(sensor_name).get("config").get(config_entry)
        )
    if device_type == "switch":
        device_config["config"]["command_topic"] = command_topic

    return device_config
