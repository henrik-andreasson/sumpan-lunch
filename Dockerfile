# Use an official Python runtime as a parent image
FROM debian:latest


WORKDIR /mylunch

# Set the working directory to /app
COPY . /mylunch/

# Install any needed packages
RUN apt-get update

RUN apt-get install --no-install-recommends -y python3 \
        sqlite3 jq python3-pip python3-setuptools  cargo \
        python3-wheel gunicorn3

RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Make port available to the world outside this container
EXPOSE 8080

COPY gunicorn-http-start.sh /mylunch/start.sh
RUN chmod +x /mylunch/start.sh


ENV FLASK_APP=mylunch.py

CMD [ "/mylunch/start.sh" ]
