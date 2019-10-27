import logging
import sys
import json
from datetime import datetime

from flask import Flask, Response, request
from reyaml import load_from_file

from structures import Tracker
import constants as c
from mqtt_client import MqttClient

log = logging.getLogger("restapi")


class Subscriber:
    def __init__(self, mqtt, config):
        """Constructor
        :param mqtt: instance of MqttClient object
        :param config: dict, the raw config (normally loaded from YAML)"""
        self.mqtt = mqtt
        self.config = config

        # this will contain the last known state of each vehicle
        self.trackers = {}

        # TODO write the ETAs in this data structure
        self.predictions = {}

    def serve(self):
        """The main loop"""
        # MQTT's loop won't block, it runs in a separate thread
        self.mqtt.set_external_handler(self.on_mqtt)
        for topic in self.config['mqtt']['topics']:
            self.mqtt.client.subscribe((topic, c.QOS_MAYBE))
        log.info('Starting MQTT loop')
        self.mqtt.client.loop_start()

    def get_tracker(self, tracker_id=None):
        '''Retrieve information about a specific vehicle
        :param tracker_id: str, tracker identifier'''
        log.debug('Get vehicle %s', tracker_id)
        if tracker_id is not None:
            try:
                return self.trackers[tracker_id].to_json()
            except KeyError:
                return Response("No such tracker", status=404)

        response = {}
        for tracker_id, meta in self.trackers.items():
            response[tracker_id] = meta.to_dict()
        return json.dumps(response)

    def index(self):
        response = {'trackers': len(self.trackers), 'predictions': len(self.predictions)}
        return json.dumps(response)

    def get_predictions_simple(self, station_id, route_id):
        """Returns a simplified structure of ETAs for the given station_id and route_id,
        the response format is as simple as possible, to make it easier to parse by certain
        type of consumers, such as scripts executed within Asterisk dial plans.

        :param station_id: int, station identifier in the DB
        :param route_id: int, route identifier
        :returns: string of the form `ETA1,ETA2,...ETAn`
        Example: `5,15,25` OR `5` OR `null` (when no ETAs available)

        Use case
        - User dials the phone number
        - User types via DTMF: <station_id>#, e.g.: 120#
        - User types via DTMF: <route_id>#, e.g.: 30#
        -> the voice machine uses text-to-speech to read out the ETAs
        """
        # If first_only is given in the request and is True, we only respond with the first ETA
        first_only = bool(request.values.get('first_only', False))
        log.debug('Get prediction station=%s, route=%s, first=%s', station_id, route_id, first_only)

        # TODO write logic to retrieve real data from the local data structures
        result = [5, 15, 25]

        if not result:
            return "null"

        if first_only:
            return str(result[0])
        else:
            return ','.join([str(item) for item in result])


    def on_mqtt(self, client, userdata, msg):
        # log.debug('MQTT IN %s %i bytes `%s`', msg.topic, len(msg.payload), repr(msg.payload))
        try:
            data = json.loads(msg.payload)
        except ValueError:
            log.debug("Ignoring bad MQTT data %s", repr(msg.payload))
            return

        if "station" in msg.topic:
            pass

        elif "transport" in msg.topic:
            # we're dealing with location data about the whereabouts of a vehicle. We update our vehicle
            # state dictionary with fresh data
            tracker_id = msg.topic.split('/')[-1]
            try:
                state = self.trackers[tracker_id]
            except KeyError:
                vehicle = Tracker(data['latitude'], data['longitude'], data['direction'], tracker_id, data['speed'])
                self.trackers[tracker_id] = vehicle
            else:
                state.latitude = data['latitude']
                state.longitude = data['longitude']
                state.direction = data['direction']
                state.speed = data['speed']
                state.timestamp = datetime.strptime(data['timestamp'], c.FORMAT_TIME)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)5s %(name)5s - %(message)s",
    )

    log.info("Starting RoataREST v%s", c.VERSION)

    config_path = sys.argv[-1]

    log.info("Processing config from `%s`", config_path)
    config = load_from_file(config_path)

    mqtt_conf = config["mqtt"]
    mqtt = MqttClient(
        name="roatarest",
        broker=mqtt_conf["host"],
        port=mqtt_conf["port"],
        username=mqtt_conf["username"],
        password=mqtt_conf["password"],
    )

    subscriber = Subscriber(mqtt, config)
    subscriber.serve()

    app = Flask('roatarest')
    app.add_url_rule('/', 'index', subscriber.index)
    app.add_url_rule('/tracker/<tracker_id>', 'tracker', subscriber.get_tracker)
    app.add_url_rule('/tracker', 'tracker_all', subscriber.get_tracker)
    app.add_url_rule('/station/<station_id>/<route_id>', 'station_eta', subscriber.get_predictions_simple)
    app.run(host="0.0.0.0", port=8000)
