#!/bin/bash

BLACKLIST_URL=https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
UNBOUND_CONF=/etc/unbound/unbound.conf.d/unbound-blacklist.conf
BLACKLIST_PATH=/tmp/unbound-blacklist.orig


# Download blacklist
echo "Downloading blacklist from $BLACKLIST_URL"
STATUS_CODE=$(curl --write-out '%{http_code}' --silent --output /dev/null $BLACKLIST_URL)
if [ $STATUS_CODE -eq 200 ]
then
  curl $BLACKLIST_URL -o $BLACKLIST_PATH > /dev/null 2>&1
  echo "Blacklist downloaded to $BLACKLIST_PATH"
else
  echo "ERROR: received http status code: $STATUS_CODE"
  exit 1
fi

# Generate unbound conf file
echo "Generating unbound config file in $UNBOUND_CONF"
echo "server:" > $UNBOUND_CONF
cat $BLACKLIST_PATH | grep '^0\.0\.0\.0' | awk '{print "    local-zone: \""$2"\" redirect\n    local-data: \""$2" A 0.0.0.0\""}' >> $UNBOUND_CONF
rm $BLACKLIST_PATH

# Validate unbound conf file
/usr/sbin/unbound-checkconf $UNBOUND_CONF
if [ $? -eq 0 ]
then
  echo "Unbound config file generated correctly at $UNBOUND_CONF"
else
  echo "Could not create unbound config file check $UNBOUND_CONF"
  exit 1
fi
