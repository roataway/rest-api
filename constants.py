VERSION = "1.2.1"

# MQTT quality of service
QOS_EXACTLY_ONCE = 2
QOS_ATLEAST_ONCE = 1
QOS_MAYBE = 0


FORMAT_TIME = '%Y-%m-%dT%H:%M:%SZ'

# route-centric telemetry
# https://github.com/roataway/api-documentation#telemetryroute
T_ROUTE_TELEMETRY = 'telemetry/route/+'

# notifications about vehicles taken off a route
# https://github.com/roataway/api-documentation#eventroute
T_ROUTE_EVENT = 'event/route/+'

ALL_TOPICS = [T_ROUTE_TELEMETRY, T_ROUTE_EVENT]