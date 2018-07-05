# How To Access EC2 Instance

`eb ssh`

## Start virtualenv for python libraries / running Django

`cd /opt/python`

`source current/env`

## Access RDS Database via psql

`psql --host=$RDS_HOSTNAME --port=$RDS_PORT --username=$RDS_USERNAME --password --dbname=$RDS_DB_NAME`

## View RDS Password

`echo $RDS_PASSWORD`