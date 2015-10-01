#!/usr/bin/env python
import os
import re
import sys
import yaml
from bs4 import BeautifulSoup

conf_path = sys.argv[1]


def read_conf(conf_path):
    return yaml.load(open(conf_path))


def find_domain_name(path):
    protocol = 'http'
    if path.startswith('http://'):
        path = path[7:]
    if path.startswith('https://'):
        protocol = 'https'
        path = path[8:]
    if path.find('/') == -1:
        return path, protocol
    else:
        return path[:path.find('/')], protocol


def get_attribute(element, attr):
    if attr == 'content':
        return element.string.strip()
    else:
        return element[attr]


def process_page(conf, name='.', address=None):
    if address is None:
        address = conf['address']
    selector = conf['selector']
    attr = conf['attr']
    download = 'download' in conf and conf['download']

    domain_name, protocol = find_domain_name(address)
    os.system('wget "%s" -O tmp' % address)
    soup = BeautifulSoup(open('tmp').read(), 'html.parser')
    os.system('rm -f tmp')
    os.system('mkdir -p "%s"' % name)
    if 'name' in conf:
        name += '/' + conf['name']
    elif 'name-selector' in conf:
        name += '/' + get_attribute(soup.select_one(conf['name-selector']), conf['name-attr'])
    for item in soup.select(selector):
        if item[attr].startswith('//'):
            full_url = protocol + ':' + get_attribute(item, attr)
        elif item[attr].startswith('/'):
            full_url = protocol + '://' + domain_name + get_attribute(item, attr)
        else:
            full_url = get_attribute(item, attr)
        if download:
            os.system('wget "%s" -P "%s"' % (full_url, name))
        if 'follow' in conf:
            process_page(conf['follow'], name, address=full_url)
        if 'recurse-condition-regex' in conf:
            pattern = re.compile(conf['recurse-condition-regex'])
            if pattern.match(full_url) is None:
                process_page(conf['recurse-final'], name, address=full_url)
            else:
                process_page(conf, name, address=full_url)


if __name__ == '__main__':
    conf = read_conf(conf_path)
    for page in conf:
        process_page(conf[page])
