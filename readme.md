Descriere generală
==================

Acest mini web-server oferă informație despre starea troleibuzelor și a timpului de așteptare în stații, printr-un REST API. Actualizarea datelor se face prin MQTT.

Utilitatea acestuia constă în:

- Obținerea unor date istorice despre poziția troleibuzelor, astfel încât https://github.com/roataway/web-ui să poată afișa ceva chiar din momentul în care pagina a fost deschisă (altfel trebuie să aștepți până când vin careva date prin websocket, pentru a desena ”coada” din spatele troleului).
- Integrarea cu sisteme terțe, pentru care există doar opțiunea HTTP, de exemplu https://github.com/roataway/voice-robot.


API'ul propriu-zis
==================

- `tracker/<tracker_id>` - returnează un JSON cu ultima informație cunoscută despre `tracker_id`. Dacă parametrul `tracker_id` e absent, va returna un JSON cu toate trackerele cunoscute.

TODO 
- ``station/<station_id>`` - returnează lista timpului de așteptare în stația respectivă, pentru toate rutele
- ``station/<station_id>/<route_id>`` - returnează lista timpului de așteptare în stația respectivă, pentru ruta respectivă
- ``stations/<route_id>`` - returnează lista identificatoarelor stațiilor asociate cu o rută specifică
- ``transport/<route_id>`` - returnează lista datelor telemetrice despre istoria pozițiilor unităților de transport de pe o rută

How to run it
=============

Prerequisites
-------------

#. Make a copy of ``res/config-sample.yaml`` to your own config file, e.g. ``config-development.yaml``, supplying the required information in the file
#. Replicate the environment using ``virtualenv`` or ``pipenv``, as described below
#. When done, run it with ``python main.py res/config-development.yaml``

The credentials as well as the server connection details are deliberately not a part of this repository. They can be found on rtec.dekart.com/infodash. The ability to figure it out on your own is the qualification barrier for getting started with this bot. Note that ``infodash`` uses WebSTOMP, rather than MQTT; however, the credentials are the same.


Virtualenv
----------

#. Create the virtualenv ``virtualenv venv-infopanel-chatbot`` to install the dependencies in it
#. Activate the venv with ``source venv-infopanel-chatbot/bin/activate``
#. Install the dependencies with ``pip install -r requirements.txt``


Pipenv
------

#. Install pipenv ``pip install pipenv``
#. Then run ``pipenv install --dev``. It will deal automatically with the venv creation and dependecy installing


How to contribute
=================

1. Run ``make autoformat`` to format all ``.py`` files
2. Run ``make verify`` and examine the output, looking for issues that need to be addressed

