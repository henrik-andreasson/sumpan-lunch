# Use an official Python runtime as a parent image
FROM debian:latest


WORKDIR /mylunch

# Set the working directory to /mylunch
COPY requirements.txt /mylunch/

# Install any needed packages
RUN apt-get update

RUN apt-get install --no-install-recommends -y python3 \
        sqlite3 jq python3-pip gnupg curl

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3 get-pip.py
RUN pip3 install -r requirements.txt --break-system-packages

RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Make port available to the world outside this container
EXPOSE 8080

COPY . /mylunch/

RUN chmod +x /mylunch/start.sh

ENV FLASK_APP=mylunch.py

CMD [ "/mylunch/start.sh" ]
