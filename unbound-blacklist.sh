#!/bin/bash

BLACKLIST_URL=https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
BLACKLIST_PATH=/etc/unbound/unbound-blacklist.orig
UNBOUND_CONF=/etc/unbound/unbound.conf.d/unbound-blacklist.conf

curl $BLACKLIST_URL -o $BLACKLIST_PATH
echo "server:" > $UNBOUND_CONF
cat $BLACKLIST_PATH | grep '^0\.0\.0\.0' | awk '{print "    local-zone: \""$2"\" redirect\n    local-data: \""$2" A 0.0.0.0\""}' >> $UNBOUND_CONF
