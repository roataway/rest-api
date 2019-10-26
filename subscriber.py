import json
import logging
from datetime import datetime

from flask import Response

import constants
from structures import Tracker

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

        self.predictions = {}

    def serve(self):
        """The main loop"""
        # MQTT's loop won't block, it runs in a separate thread
        self.mqtt.set_external_handler(self.on_mqtt)
        for topic in self.config['mqtt']['topics']:
            self.mqtt.client.subscribe((topic, constants.QOS_MAYBE))
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

