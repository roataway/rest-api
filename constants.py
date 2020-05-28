VERSION = "1.1.0"

# MQTT quality of service
QOS_EXACTLY_ONCE = 2
QOS_ATLEAST_ONCE = 1
QOS_MAYBE = 0


FORMAT_TIME = '%Y-%m-%dT%H:%M:%SZ'



T_STATION_ETA = 'state/station/+'
T_TRACKER_TELEMETRY = 'telemetry/transport/+'
T_ROUTE_TELEMETRY = 'telemetry/route/+'
T_ROUTE_EVENT = 'event/route/+'

ALL_TOPICS = [T_STATION_ETA, T_TRACKER_TELEMETRY, T_ROUTE_TELEMETRY, T_ROUTE_EVENT]