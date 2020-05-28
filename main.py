import logging
import sys
import json
from datetime import datetime
import os
import argparse
from collections import defaultdict

from flask import Flask, Response
import waitress
from reyaml import load_from_file

from structures import Tracker
import constants as c
from mqtt_client import MqttClient

log = logging.getLogger("restapi")


class Subscriber:
    def __init__(self, mqtt):
        """Constructor
        :param mqtt: instance of MqttClient object"""
        self.mqtt = mqtt

        # this will contain the last known state of each vehicle
        self.trackers = {}

        # keep track of the time when the server was started, which might
        # be useful when troubleshooting behaiour on Heroku (perhaps it
        # stopped the application, so the state was lost)
        self.started_at = datetime.utcnow()

        # dict that maps a route ID as a string, to a set of trackerIDs that belong to that route
        self.routes = defaultdict(set)

    def serve(self):
        """The main loop"""
        # MQTT's loop won't block, it runs in a separate thread
        self.mqtt.set_external_handler(self.on_mqtt)
        for topic in c.ALL_TOPICS:
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

    def get_route_tracker(self, route_id):
        '''Retrieve information about all trackers on a specific route
        :param route_id: int, route id'''
        try:
            trackers_on_route = self.routes[route_id]
        except KeyError:
            return Response("No such route", status=404)
        else:
            response = {}
            for tracker_id in trackers_on_route:
                try:
                    response[tracker_id] = self.trackers[tracker_id].to_dict()
                except KeyError:
                    # this should never happen, but if it does, we remove it from
                    # the route set
                    log.debug('Referencing unknwon tracker %s', tracker_id)
                    self.routes[route_id].remove(tracker_id)

            return Response(json.dumps(response), mimetype='application/json')

    def index(self):
        response = f"v{c.VERSION} running since {self.started_at.strftime('%d %b %H:%M')}\ntrackers: {len(self.trackers)}"
        return Response(response, mimetype='text/plain')


    def on_mqtt(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
        except ValueError:
            log.debug("Ignoring bad MQTT data %s", repr(msg.payload))
            return

        if 'route' in msg.topic:
            # this is route-specific location data
            route_id = msg.topic.split('/')[-1]
            tracker_id = data['rtu_id']
            try:
                state = self.trackers[tracker_id]
            except KeyError:
                vehicle = Tracker(data['latitude'], data['longitude'], data['direction'], data['board'], tracker_id, data['speed'])
                self.trackers[tracker_id] = vehicle
            else:
                state.latitude = data['latitude']
                state.longitude = data['longitude']
                state.direction = data['direction']
                state.speed = data['speed']
                state.timestamp = datetime.strptime(data['timestamp'], c.FORMAT_TIME)

            self.routes[route_id].add(tracker_id)
            return

        if 'event' in msg.topic:
            # this is a notification that tells us that a vehicle was removed from a route
            route_id = msg.topic.split('/')[-1]
            self.routes[route_id].remove(tracker_id = data['rtu_id'])
            return


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)5s %(name)5s - %(message)s",
    )

    log.info("Starting RoataREST v%s", c.VERSION)

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to config file', type=str, default='')
    args = parser.parse_args()


    if args.config:
        log.info("Processing config from `%s`", args.config)
        config = load_from_file(args.config)
    else:
        log.info("Using config from environment variables")
        # These are taken from https://github.com/roataway/api-documentation and are
        # assumed constant
        config = {'host': os.getenv('MQTT_HOST', 'opendata.dekart.com'),
                  'port': os.getenv('MQTT_PORT', 1945),
                  'username': os.getenv('MQTT_USER', None),
                  'password': os.getenv('MQTT_PASS', None),
                  }

    mqtt = MqttClient(
        name="roatarest",
        broker=config["host"],
        port=config["port"],
        username=config["username"],
        password=config["password"]
    )

    subscriber = Subscriber(mqtt)
    subscriber.serve()

    app = Flask('roatarest')
    app.add_url_rule('/', 'index', subscriber.index)
    app.add_url_rule('/route/<route_id>/trackers', 'tracker_route', subscriber.get_route_tracker)

    # these two might be unnecessary, leaving them enabled for now, let's see if there is an
    # actual demand for these
    app.add_url_rule('/tracker/<tracker_id>', 'tracker', subscriber.get_tracker)
    app.add_url_rule('/tracker', 'tracker_all', subscriber.get_tracker)

    # To run this on Heroku, we have to use whatever port they've allocated for us,
    # otherwise use a default port number (e.g., when testing locally)
    listen_port = os.getenv('PORT', 8080)
    waitress.serve(app, listen='*:%s' % listen_port)
