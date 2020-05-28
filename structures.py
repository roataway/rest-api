import logging
import json
from datetime import datetime
from dataclasses import dataclass

import constants as c

log = logging.getLogger("struct")


@dataclass
class Route:
    # human-readable name of the route, usually it is a number like "30",
    # but we still treat them as strings, because they can be something like "30A"
    name: str

    # a list of strings that contains 2 items, corresponding to the directions
    # of the route, e.g. `airport->center` and `center->airport`
    segments: list

    # the id of the station which marks the beginning of the second segment
    cutoff_station_id: int

    # list of station IDs, arranged in the sequence that corresponds to
    # this particular route. Note that some stations can be a part of different
    # routes, though they will most likely have a different order number in
    # each of the sequences
    station_sequence: list

    # this list contains board numbers, as strings, of transports that are
    # assigned to this route. This is RFU, in case we end up with a bazillion
    # transports, and forming a location message would require iterating through
    # the entire transport dict just to know which transport corresponds to
    # a given route
    transports: list = None


@dataclass
class Tracker:
    latitude: float = None
    longitude: float = None
    # where it goes, North=0, West=270, South=180, East=90
    direction: float = None
    # usually numeric, this is the number written on the trolleybus, e.g. "3913",
    # but we have to assume the can contain non-digit characters
    board_name: str = None
    # human-readable RTU_ID
    tracker_id: str = None
    speed: int = 0
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow()

    def to_json(self):
        result = {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "direction": self.direction,
            "board": self.board_name,
            "speed": self.speed,
            "timestamp": self.timestamp.strftime(c.FORMAT_TIME),
        }
        return json.dumps(result)

    def to_dict(self):
        result = {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "direction": self.direction,
            "board": self.board_name,
            "speed": self.speed,
            "timestamp": self.timestamp.strftime(c.FORMAT_TIME),
        }
        return result
