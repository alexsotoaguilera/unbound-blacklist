#!/usr/bin/env python

import sys
import os
import shutil
import tempfile
import configparser
import urllib.request


CONF_PATH = '/etc/unbound-blacklist/unbound-blacklist.conf'


def download_bl_raw(url):
    # Download blacklist
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print("Error: can't download blacklist from {}, error code {}".format(url, e.code))
        return None
    except urllib.error.URLError as e:
        print("Error: can't download blacklist from {}, reason {}".format(url, e.reason))
        return None
    # Save list to tmp file in disk
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        shutil.copyfileobj(response, tmp_file)
    return tmp_file.name


def parse_domain(bl_format, bl_line):
    domain = None
    if bl_format == '0.0.0.0 DOMAIN':
        if len(bl_line.split(' ')) == 2 and bl_line.split(' ')[0] == '0.0.0.0':
            if bl_line.split(' ')[1].rstrip() != '0.0.0.0':
                domain = bl_line.split(' ')[1].rstrip()
    elif bl_format == 'DOMAIN':
        if not bl_line.startswith('#') and bl_line.rstrip() != '':
            domain = bl_line.rstrip()
    else:
        print("Warning: unknown blacklist format \"{}\".".format(bl_format))
    return domain


def gen_unbound_bl_file(bl_raw_path, blocking_mode, bl_format, wl_path):
    # load whitelist
    whitelisted_domains = []
    if os.path.isfile(wl_path):
        with open(wl_path) as f:
            whitelisted_domains = [line.rstrip() for line in f if not line.startswith('#') and line != '\n']
    # generate unbound blacklist config file
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as bl_unbound_file:
        bl_unbound_file.write("server:\n")
        with open(bl_raw_path) as f:
            for line in f:
                domain = parse_domain(bl_format, line)
                if domain is not None and domain not in whitelisted_domains:
                    bl_unbound_file.write("    local-zone: \"{}\" {}\n".format(domain, blocking_mode))
    os.remove(bl_raw_path)
    return bl_unbound_file.name


def validate_unbound_config(bl_conf_file):
    cmd = "/usr/sbin/unbound-checkconf {}".format(bl_conf_file)
    status = os.system(cmd)
    return status


if __name__ == "__main__":
    # Check default config file
    if os.path.isfile(CONF_PATH) is False:
        print("Error: config file {} doesn't exists.".format(CONF_PATH))
        sys.exit(100)
    config = configparser.ConfigParser()
    config.read(CONF_PATH)
    blocking_mode = config['DEFAULT'].get('blocking_mode', 'always_nxdomain')
    if blocking_mode not in ('always_nxdomain', 'always_nodata'):
        print("Error: blocking_mode must be 'always_nxdomain' or 'always_nodata'")
        sys.exit(100)
    bl_conf_path = config['DEFAULT'].get('unbound_conf_path', '/etc/unbound/unbound.conf.d/')
    if os.path.isdir(bl_conf_path) is False:
        print("Error: specified 'unbound_conf_path' is not a valid directory.")
        sys.exit(100)
    wl_path = config['DEFAULT'].get('whitelist_path', '/etc/unbound-blacklist/whitelist')
    if os.path.isfile(bl_conf_path) is False:
        print("Warning: specified 'whitelist_path' is not a valid file.")

    # Check blacklist sections in config file
    for blacklist_conf in config.sections():
        if config[blacklist_conf].getboolean('enabled'):
            print("Info: configuration enabled for {}.".format(blacklist_conf))
            bl_url = config[blacklist_conf]['url']
            bl_conf = config[blacklist_conf]['config']
            bl_format = config[blacklist_conf]['input_format']
            print("Info: downloading blacklist {}.".format(bl_url))
            bl_raw_path = download_bl_raw(bl_url)
            if bl_raw_path is None:
                sys.exit(100)
            bl_conf_path = gen_unbound_bl_file(bl_raw_path, blocking_mode, bl_format, wl_path)
            if validate_unbound_config(bl_conf_path) != 0:
                print("Error: invalid unbound config file, check blacklist origin")
                os.remove(bl_conf_path)
                sys.exit(100)
            else:
                shutil.move(bl_conf_path, os.path.join(bl_conf_path, bl_conf))