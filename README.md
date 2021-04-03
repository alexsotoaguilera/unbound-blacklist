# unbound-blacklist
Service that generate and update a blacklist for unbound DNS server

### How it works:

1. Download blacklist
2. Generate **unbound** blacklist configuration
3. Reload **unbound** service
4. On boot time or after 24 hours, the configured timer updates the blacklist

### Installation with **deb** package
Clone the repository
```
git clone https://github.com:alexsotoaguilera/unbound-blacklist.git
```

Generate deb package
```
cd unbound-blacklist
dpkg-deb --build --root-owner-group unbound-blacklist
```
Install deb package
```
sudo dpkg -i unbound-blacklist.deb
```

### Manual installation:
Clone the repository
```
git clone https://github.com:alexsotoaguilera/unbound-blacklist.git
```

Copy script to /usr/local/bin/
```
sudo cp unbound-blacklist/unbound-blacklist/usr/local/bin/unbound-blacklist.sh /usr/local/bin/
sudo chmod ug+x /usr/local/bin/unbound-blacklist.sh
```

Copy service and timer to /etc/systemd/system/
```
sudo cp unbound-blacklist/unbound-blacklist/etc/systemd/system/unbound-blacklist-updater.service /etc/systemd/system/
sudo cp unbound-blacklist/unbound-blacklist/etc/systemd/system/unbound-blacklist-updater.timer /etc/systemd/system/
```

Enable service and timer
```
sudo systemctl enable unbound-blacklist-updater.service
sudo systemctl enable unbound-blacklist-updater.timer
```

Start service and timer
```
sudo systemctl start unbound-blacklist-updater.service
sudo systemctl start unbound-blacklist-updater.timer
```

### Configuration

Edit script variables
```
sudo vi /usr/local/bin/unbound-blacklist.sh

BLACKLIST_URL=https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts  # the hosts blacklist URL
UNBOUND_CONF=/etc/unbound/unbound.conf.d/unbound-blacklist.conf                 # place to save unbound blacklist conf
```

Restart service and timer
```
sudo systemctl restart unbound-blacklist-updater.service
sudo systemctl restart unbound-blacklist-updater.timer
```

and that's it
