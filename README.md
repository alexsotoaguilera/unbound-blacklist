# unbound-blacklist
Service that generate and update a blacklist for unbound DNS server
- supports multiple blacklists
- supports domain whitelist
- TODO: merge blacklists to prevent redundancy

### How it works:

1. Download configured blacklists.
2. Generate **unbound** blacklist configuration without whitelisted domains.
3. Reload **unbound** service.
4. After 15 minutes from the system boot and every 24 hours, the systemd timer updates the blacklist.

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
sudo cp unbound-blacklist/unbound-blacklist/usr/local/bin/unbound-blacklist /usr/local/bin/
sudo chmod ug+x /usr/local/bin/unbound-blacklist
```

Copy config files to /etc/
```
sudo cp unbound-blacklist/etc/unbound-blacklist /etc/
```

Copy service and timer to /etc/systemd/system/
```
sudo cp unbound-blacklist/unbound-blacklist/etc/systemd/system/unbound-blacklist-updater.service /etc/systemd/system/
sudo cp unbound-blacklist/unbound-blacklist/etc/systemd/system/unbound-blacklist-updater.timer /etc/systemd/system/
```

Enable timer
```
sudo systemctl enable unbound-blacklist-updater.timer
```

Start service and timer
```
sudo systemctl start unbound-blacklist-updater.service
sudo systemctl start unbound-blacklist-updater.timer
```

### Configuration
Edit configuration at /etc/unbound-blacklist/conf.json
```
{
  "blocking_mode": "always_nxdomain",
  "unbound_conf_path": "/etc/unbound/unbound.conf.d/",
  "whitelist_path": "/etc/unbound-blacklist/whitelist",

  "blacklist":{
    "stevenblack": {
      "enabled": true,
      "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
      "input_format": "0.0.0.0 DOMAIN",
      "config": "/etc/unbound/unbound.conf.d/unbound-blacklist_stevenblack.conf"
    },
    "oisd": {
      "enabled": false,
      "url": "https://dbl.oisd.nl/",
      "input_format": "DOMAIN",
      "config": "/etc/unbound/unbound.conf.d/unbound-blacklist_oisd.conf"
    }
  }
}
```

### Whitelist
Add on domain per line on /etc/unbound-blacklist/whitelist
```
example1.com
example2.com
```


Rebuild blacklist files:
```
sudo unbound-blacklist
```

and that's it
