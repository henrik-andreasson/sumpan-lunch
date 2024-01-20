#!/bin/bash

if [ "x$CERT" != "x" ] ; then
  echo "$CERT" | tr ';' '\n' > /mylunch/cert.pem
fi

if [ "x$CA" != "x" ] ; then
  echo "$CA" | tr ';' '\n' > /mylunch/ca.pem
fi

if [ "x$KEY" != "x" ] ; then
  echo "$KEY" | tr ';' '\n' > /mylunch/key.pem
fi

gunicorn mylunch:app -b 0.0.0.0:443 \
         --pid /mylunch/mylunch.pid \
         --keyfile /mylunch/key.pem  \
         --certfile  /mylunch/cert.pem
