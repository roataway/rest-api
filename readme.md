Descriere generală
==================

Acest mini web-server oferă informație despre starea troleibuzelor și (TODO) a timpului de așteptare în stații, printr-un REST API. Actualizarea datelor se face prin MQTT.

Utilitatea acestuia constă în:

- Obținerea unor date istorice despre poziția troleibuzelor, astfel încât https://github.com/roataway/web-ui să poată afișa ceva chiar din momentul în care pagina a fost deschisă (altfel trebuie să aștepți până când vin careva date prin websocket).
- Integrarea cu sisteme terțe, pentru care există doar opțiunea HTTP, de exemplu https://github.com/roataway/voice-robot.


API'ul propriu-zis
==================

`/` informație generală
-----------------------

Returnează un text în care se vede versiunea aplicației, data lansării și numărul de trackere cunoscute. Exemplu:

```
v1.2.0 running since 28 May 12:48
trackers: 220
```


`tracker/<tracker_id>` date despre un tracker
---------------------------------------------

Returnează un JSON cu ultima informație cunoscută despre `tracker_id`. Dacă parametrul `tracker_id` e absent, va returna un JSON cu toate trackerele cunoscute. Opțiunea cea din urmă va genera un răspuns mare și nu ar trebui să fie abuzată. Exemplu de răspuns:

```
{"longitude": 28.935659, "latitude": 46.935407, "direction": 0, "board": "3917", "speed": 0, "timestamp": "2020-05-28T13:02:10Z"}
```



`route/<route_id>/trackers` trackere pe o rută
----------------------------------------------

Returnează un JSON cu ultima informație despre fiecare tracker asociat cu ruta dată.

Exemplu de răspuns:

```
{
   "010":{
      "longitude":28.906452,
      "latitude":46.954408,
      "direction":133,
      "board":"3917",
      "speed":43,
      "timestamp":"2020-05-28T12:50:55Z"
   },
   "005":{
      "longitude":28.829662,
      "latitude":47.022516,
      "direction":0,
      "board":"3901",
      "speed":0,
      "timestamp":"2020-05-28T12:50:41Z"
   }
}
```


How to run it
=============

Prerequisites
-------------

1. Make a copy of `res/config-sample.yaml` to your own config file, e.g. `config-development.yaml`, supplying the required information in the file
2. Replicate the environment using `virtualenv` or `pipenv`, as described below
3. When done, run it with `python main.py res/config-development.yaml`

- The credentials as well as the server connection details are given in the [API documentation](https://github.com/roataway/api-documentation)
- Information about [routes and vehicles](https://github.com/roataway/infrastructure-data)


Virtualenv
----------

1. Create the virtualenv `virtualenv venv-roatarest` to install the dependencies in it
2. Activate the venv with `source venv-roatarest/bin/activate`
3. Install the dependencies with `pip install -r requirements.txt`


Pipenv
------

1. Install pipenv `pip install pipenv`
2. Then run `pipenv install --dev`. It will deal automatically with the venv creation and dependecy installing


How to contribute
=================

1. Run `make autoformat` to format all `.py` files
2. Run `make verify` and examine the output, looking for issues that need to be addressed

