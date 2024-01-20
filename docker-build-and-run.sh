#!/bin/bash

docker build -t mylunch  .

docker run -p5000:5000 -it  --mount type=bind,source="$(pwd)",target=/mylunch mylunch flask run --host=0.0.0.0 --reload
