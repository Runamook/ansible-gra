#!/bin/bash

PYTHONPATH=/opt/graphite/webapp django-admin.py migrate --settings=graphite.settings --run-syncdb

sudo cp -r /opt/graphite/webapp/content/* /opt/graphite/static/

#curl -XPOST -H "Accept: application/json" -H "Content-Type: application/json" http://admin:admin@192.168.33.4:3000/api/datasources -d '{
#  "isDefault" : true,
#  "name":"local_graphite",
#  "type":"graphite",
#  "url":"http://localhost",
#  "access":"proxy",
#  "basicAuth":false,
#  "jsonData" : {
#          "graphiteVersion" : "1.0"
#}}'
