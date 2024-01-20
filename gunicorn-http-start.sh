#!/bin/bash

gunicorn mylunch:app -b 0.0.0.0:8080 \
         --pid /mylunch/mylunch.pid 
