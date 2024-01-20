# About

Schema service for multiple teams with on-call planning.

Also can announce new/changes work and on-call to Rocket.Chat

REST API for adding work and users exist, see utils/

This is an early version but working software.

Author: https://github.com/henrik-andreasson/

Heavily based on the excellent tutorial  [Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) by Miguel Grinberg.

Big Thanks to Miguel!


# pictures

## first page / month view
![first page](docs/first-page.png)

![month-view](docs/month-view.png)

## On call
![on-call](docs/oncall.png)

## stats
![stats](docs/stats.png)

## Non Working days
![Non Working Days](docs/nwd.png)

## absence
![Absennse](docs/absence.png)

# Run on CentOS

Install python3 and sqlite

    yum install -y python3 sqlite

Used modules

    pip3 install flask-sqlalchemy flask-migrate flask-login flask-mail \
  flask-bootstrap flask-moment flask-babel python-dotenv jwt flask-wtf \
  WTForms-Components flask-httpauth rocketchat_API icalendar gunicorn \
  email_validator PyMysql

install source

    mkdir /opt/mylunch
    cd /opt/mylunch
    unzip mylunch-x.y.z.zip

start
    export FLASK_APP=mylunch.py
    cd /opt/mylunch
    flask run --host=0.0.0.0

See also the systemd service file mylunch.service to run with gunicorn

# Run in Docker

build docker:

    docker build -t mylunch  .

Run bash in docker:

    docker run -p5000:5000 -it  --mount type=bind,source="$(pwd)",target=/mylunch mylunch bash

Run flask

    docker run -p5000:5000 -it  --mount type=bind,source="$(pwd)",target=/mylunch mylunch flask run --host=0.0.0.0 --reload
