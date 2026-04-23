import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Type, Union
import pytz

# configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# template definitions
TEMPLATE_TIME_MS: str = '<TIME_MS>'
TEMPLATE_TIME_STR: str = '<TIME_STR>'

# MAPPING TEMPLATES
OBSERVATION_TEMPLATE_CONTEXT_DAHCC: str = """
<https://dahcc.idlab.ugent.be/Protego/_participant1/obs%s> <http://rdfs.org/ns/void#inDataset> <https://dahcc.idlab.ugent.be/Protego/_participant1> .
<https://dahcc.idlab.ugent.be/Protego/_participant1/obs%s> <https://saref.etsi.org/core/measurementMadeBy> <https://dahcc.idlab.ugent.be/Homelab/SensorsAndActuators/%s> .
<https://dahcc.idlab.ugent.be/Protego/_participant1/obs%s> <http://purl.org/dc/terms/isVersionOf> <https://saref.etsi.org/core/Measurement> .
<https://dahcc.idlab.ugent.be/Protego/_participant1/obs%s> <https://saref.etsi.org/core/relatesToProperty> <https://dahcc.idlab.ugent.be/Homelab/SensorsAndActuators/%s> .
<https://dahcc.idlab.ugent.be/Protego/_participant1/obs%s> <https://saref.etsi.org/core/hasTimestamp> "%s"^^<http://www.w3.org/2001/XMLSchema#dateTime> .
<https://dahcc.idlab.ugent.be/Protego/_participant1/obs%s> <https://saref.etsi.org/core/hasValue> "%s"^^<http://www.w3.org/2001/XMLSchema#float> .
"""

VALUE_TEMPLATE: str = "\"%s\"^^%s"

# CONVERTERS OF JSON VALUES TO ONTOLOGY CONCEPTS
METRIC_TYPES_CONTEXT: Dict[str, Type] = {
    "airquality.co2": float,
    "airquality.voc_total": bool,
    "energy.consumption": float,
    "energy.power": float,
    "environment.blind": float,
    "environment.button": bool,
    "environment.dimmer": float,
    "environment.light": float,
    "environment.lightswitch": bool,
    "environment.motion": bool,
    "environment.open": bool,
    "environment.relativehumidity": float,
    "environment.relay": bool,
    "environment.temperature": float,
    "environment.voltage": float,
    "environment.waterRunning::bool": bool,
    "mqtt.lastMessage": str,
    "org.dyamand.aqura.AquraLocationState_Protego User": str,
    "org.dyamand.aqura.AquraLocationState_Protego_User": str,
    "org.dyamand.types.airquality.CO2": float,
    "org.dyamand.types.common.AtmosphericPressure": float,
    "org.dyamand.types.common.Loudness": float,
    "org.dyamand.types.common.RelativeHumidity": float,
    "org.dyamand.types.common.Temperature": float,
    "people.presence.detected": bool,
    "people.presence.numberDetected": float,
    "weather.pressure": float,
    "weather.rainrate": float,
    "weather.windspeed": float,
    "org.dyamand.types.health.SpO2": float
}

METRIC_TYPES_WEARABLE: Dict[str, Type] = {
    "org.dyamand.types.health.BodyTemperature": float,
    "org.dyamand.types.common.Load": float,
    "org.dyamand.types.health.DiastolicBloodPressure": float,
    "org.dyamand.types.health.HeartRate": float,
    "org.dyamand.types.health.SystolicBloodPressure": float,
    "org.dyamand.types.health.GlucoseLevel": float,
    "smartphone.acceleration.x": float,
    "smartphone.acceleration.y": float,
    "smartphone.acceleration.z": float,
    "smartphone.ambient_light": float,
    "smartphone.ambient_noise.amplitude": float,
    "smartphone.ambient_noise.frequency": float,
    "smartphone.application": str,
    "smartphone.gravity.x": float,
    "smartphone.gravity.y": float,
    "smartphone.gravity.z": float,
    "smartphone.gyroscope.x": float,
    "smartphone.gyroscope.y": float,
    "smartphone.gyroscope.z": float,
    "smartphone.keyboard": str,
    "smartphone.linear_acceleration.x": float,
    "smartphone.linear_acceleration.y": float,
    "smartphone.linear_acceleration.z": float,
    "smartphone.location.accuracy": float,
    "smartphone.location.altitude": float,
    "smartphone.location.bearing": float,
    "smartphone.location.latitude": float,
    "smartphone.location.longitude": float,
    "smartphone.magnetometer.x": float,
    "smartphone.magnetometer.y": float,
    "smartphone.magnetometer.z": float,
    "smartphone.proximity": float,
    "smartphone.rotation.x": float,
    "smartphone.rotation.y": float,
    "smartphone.rotation.z": float,
    "smartphone.screen": str,
    "smartphone.sleepAPI.API_confidence": float,
    "smartphone.sleepAPI.model_type": str,
    "smartphone.sleepAPI.t_start": float,
    "smartphone.sleepAPI.t_stop": float,
    "smartphone.step": float,
    "wearable.acceleration.x": float,
    "wearable.acceleration.y": float,
    "wearable.acceleration.z": float,
    "wearable.battery_level": float,
    "wearable.bvp": float,
    "wearable.gsr": float,
    "wearable.ibi": float,
    "wearable.on_wrist": bool,
    "wearable.skt": float
}

SENSOR_SUFFIX_MAP: Dict[str, str] = {
    "org.dyamand.aqura.AquraLocationState_Protego_User": "Tag",
    "wearable.acceleration.x": 'Accelerometer',
    "wearable.acceleration.y": 'Accelerometer',
    "wearable.acceleration.z": 'Accelerometer',
    "wearable.battery_level": 'BatteryLevelMeter',
    "wearable.bvp": 'PPGSensor',
    "wearable.gsr": 'GSRSensor',
    "wearable.ibi": 'PPGSensor',
    "wearable.on_wrist": 'OnWristDetector',
    "wearable.skt": 'Thermopile'
}

TYPE_MAP: Dict[Type, str] = {
    float: "<http://www.w3.org/2001/XMLSchema#float>",
    int: "<http://www.w3.org/2001/XMLSchema#integer>",
    bool: "<http://www.w3.org/2001/XMLSchema#integer>",
    str: "<http://www.w3.org/2001/XMLSchema#string>"
}

uuid_map: Dict[str, int] = {}

def generate_uuid(metric_id: str, patient_id: str) -> int:
    """
    Generates a unique incremental ID for a given patient.
    
    Args:
        metric_id: The ID of the metric being recorded.
        patient_id: The ID of the patient.
        
    Returns:
        A unique integer ID for this patient's observation.
    """
    key = '%s' % (patient_id)
    if key not in uuid_map:
        uuid_map[key] = 0
    result = uuid_map[key]
    uuid_map[key] += 1
    return result

def remove_whitespace(given_str: str) -> str:
    """
    Collapses all whitespace in a string into single spaces.
    
    Args:
        given_str: The string to clean.
        
    Returns:
        The cleaned string.
    """
    return ' '.join(given_str.split())

def update_source_id(source_id: str, metric_id: str) -> str:
    """
    Appends a sensor-specific suffix to a source ID based on the metric.
    
    Args:
        source_id: The original source/sensor ID.
        metric_id: The metric ID to check for a suffix.
        
    Returns:
        The updated source ID with an optional suffix.
    """
    if metric_id in SENSOR_SUFFIX_MAP:
        return '%s.%s' % (source_id, SENSOR_SUFFIX_MAP[metric_id])
    else:
        return source_id

def map_value(value: Any, metric_id: str) -> Tuple[str, Optional[str]]:
    """
    Maps a raw value to its RDF literal representation and determines its metric group.
    
    Args:
        value: The raw value (float, bool, or str).
        metric_id: The metric ID to determine type and group.
        
    Returns:
        A tuple containing (RDF literal string, metric group name).
    """
    value_type, metric_group = float, None
    if metric_id in METRIC_TYPES_CONTEXT:
        value_type, metric_group = METRIC_TYPES_CONTEXT[metric_id], "CONTEXT"
    elif metric_id in METRIC_TYPES_WEARABLE:
        value_type, metric_group = METRIC_TYPES_WEARABLE[metric_id], "WEARABLE"

    if value_type == bool:
        processed_value = int(1) if value == 1 or value == '1' else int(0)
    else:
        processed_value = value

    return VALUE_TEMPLATE % (processed_value, TYPE_MAP.get(value_type, TYPE_MAP[str])), metric_group

def map_observation(metric_id: str, source_id: str, value: Any, timestamp: Optional[str]) -> Optional[str]:
    """
    Maps a single sensor observation to an RDF N-Triples string.
    
    Args:
        metric_id: The metric identifier.
        source_id: The sensor identifier (usually 'patient.sensor').
        value: The observed value.
        timestamp: The ISO-formatted timestamp.
        
    Returns:
        An N-Triples formatted string representing the observation, or None if mapping fails.
    """
    # extract patient ID from source ID
    # Handle both . and : as separators
    if ":" in source_id:
        split = source_id.split(":", 1)
    elif "." in source_id:
        split = source_id.split(".", 1)
    else:
        split = ["Unknown", source_id]
        
    patient_id = split[0]
    local_source_id = split[1]

    # replace spaces by underscores in metricId
    metric_id = metric_id.replace(' ', '_')

    # add suffix to sensor (sourceId) based on metricId
    local_source_id = update_source_id(local_source_id, metric_id)

    # generate timestamp
    uuid = generate_uuid(metric_id, patient_id)
    
    timestamp_utc = timestamp if timestamp else TEMPLATE_TIME_MS

    # map value
    _, metric_group = map_value(value, metric_id)

    # create RDF data
    if metric_group in ["CONTEXT", "WEARABLE"]:
        return OBSERVATION_TEMPLATE_CONTEXT_DAHCC % (
            uuid, uuid, local_source_id,
            uuid, uuid, metric_id,
            uuid, str(timestamp_utc),
            uuid, value
        )
    return None

def annotate_event(event: Dict[str, Any], template_timestamps: bool = False) -> Optional[str]:
    """
    High-level function to annotate a JSON-like event into RDF.
    
    Args:
        event: A dictionary containing 'sourceId', 'metricId', 'value', and optionally 'timestamp'.
        template_timestamps: If True, uses a template placeholder for timestamps.
        
    Returns:
        A cleaned N-Triples string or None.
    """
    try:
        # check if event is valid
        valid = 'sourceId' in event and \
                'metricId' in event and \
                'value' in event and \
                ('timestamp' in event or template_timestamps)

        if not valid:
            return None

        # otherwise, return mapped event
        rdf_event = map_observation(
            metric_id=event['metricId'],
            source_id=event['sourceId'],
            value=event['value'],
            timestamp=event['timestamp'] if not template_timestamps else None
        )
        return remove_whitespace(rdf_event) if rdf_event is not None else rdf_event

    except Exception as e:
        logger.error(f"Error annotating event: {e}")
        return None
