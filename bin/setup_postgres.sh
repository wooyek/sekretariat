#!/usr/bin/env bash
#
# This script will install and setup PostgreSQL
#

echo "------> Installing postgresql "
sudo apt-get install -y postgresql postgresql-contrib postgis
sudo ufw allow 5432

ENV=$(dirname $(dirname $(readlink -fm $0)))/.env
echo "------> Loading env ${ENV}"
source <(sed -e /^$/d -e /^#/d -e 's/.*/declare -x "&"/g' .env)

echo "------> Setting up host in pg_hba.conf"
echo ${DATABASE_CLIENT_HOST} | sudo tee -a /etc/postgresql/9.5/main/pg_hba.conf
echo "------> Setting up listen_addresses in postgresql.conf"
echo "listen_addresses = '*'" | sudo tee -a /etc/postgresql/9.5/main/postgresql.conf

# Restart database for configurations settings to take effect
sudo /etc/init.d/postgresql restart

echo "------> Setting up postgis extension"
# First you need to enable postgis for all new databases. This will remove superuser requirement during db initialization
# http://stackoverflow.com/a/35209186/260480
sudo -u postgres -E psql -d template1 -c "CREATE EXTENSION IF NOT EXISTS postgis;"
