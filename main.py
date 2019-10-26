import logging
import sys
from datetime import datetime

from flask import Flask
from reyaml import load_from_file

import constants as c
from mqtt_client import MqttClient
from subscriber import Subscriber

log = logging.getLogger("restapi")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(name)5s - %(message)s"
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

    subscriber = Subscriber(mqtt, config["mqtt"]["topics"])
    subscriber.serve()

    app = Flask("roatarest")
    app.url_map.strict_slashes = False
    app.add_url_rule("/", "index", subscriber.index)
    app.add_url_rule("/tracker/<tracker_id>", "tracker", subscriber.get_tracker)
    app.add_url_rule("/tracker", "tracker_all", subscriber.get_tracker)
    app.run(host="0.0.0.0", port=8000)
