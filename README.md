# magenta session

The code to session with [magenta](https://github.com/tensorflow/magenta).  
Do you have any MIDI instrument? If then, you can do call & response with magenta!  
(You don't have such instruments? Of course, you can play this without it!)

**You can see the sample play from here**

* [Playing Vide](https://youtu.be/owOI2CMavoE)
* [Recorded Session](https://soundcloud.com/icoxfog417/magenta-sessioned-track)

(Sorry about my poor keyboard play!)

You can deploy your own Magenta Session to Heroku by following button.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Architecture

![architecture.PNG](./docs/architecture.PNG)

The model is ported from [ai-duet](https://github.com/googlecreativelab/aiexperiments-ai-duet).

## How to use

1. Install `magenta_session`
2. Run `python server/server.py`
3. Access the [Server(localhost:8080)](http://localhost:8080)
4. Session Now! (please refer following image).

![gui.PNG](./docs/gui.PNG)


## Install 

`magenta_session` depends on TensorFlow and magenta.  
Please refer [magenta installation guide](https://github.com/tensorflow/magenta#installation).

Dependencies

Python

* [magenta](https://github.com/tensorflow/magenta)
* [TensorFlow](https://github.com/tensorflow/tensorflow)
* [Flask](https://github.com/pallets/flask)

JavaScript

* [Tone.js](https://github.com/Tonejs/Tone.js)
* [MidiConvert](https://github.com/Tonejs/MidiConvert)
* [jQuery](https://github.com/jquery/jquery)

CSS

* [Bulma](http://bulma.io/)

## Docker
Docker is an open-source containerization software which simplifies installation across various OSes.Once you have Docker installed, you can just run:

```bash
$ docker run -it -p 80:8080 asashiho/magenta_session
```

If you want to build DockerImage yourself, you can just run:

```bash
$ docker build -t magenta_session .
$ docker run -it -p 80:8080 magenta-session
```

You can now play with `magenta_session` at `http://<docker-server-ipaddress>/`.


Session Now!Enjoy Music!
