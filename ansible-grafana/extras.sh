#!/bin/bash

PYTHONPATH=/opt/graphite/webapp django-admin.py migrate --settings=graphite.settings --run-syncdb

sudo cp -r /opt/graphite/webapp/content/* /opt/graphite/static/
