import os
import re
import sys
import yaml
from bs4 import BeautifulSoup


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


def get_value(element, conf):
    if 'attribute' in conf:
        return element[conf['attribute']]
    else:
        return element.contents[0].strip()

def select(soup, conf, select_one=False):
    if select_one:
        selected_element = soup.select_one(conf['css-selector'])
        return get_value(selected_element, conf)
    selected_elements = soup.select(conf['css-selector'])
    values = []
    for element in selected_elements:
        values.append(get_value(element, conf))
    return values


def process_page(conf, name='.', address=None):
    if address is None:
        address = conf['address']
    download = 'download' in conf and conf['download']
    wget_extra_args = ''
    if 'wget-extra-args' in conf:
        wget_extra_args = conf['wget-extra-args']

    domain_name, protocol = find_domain_name(address)
    os.system('wget %s "%s" -O tmp' % (wget_extra_args, address))
    soup = BeautifulSoup(open('tmp').read(), 'html.parser')
    os.system('rm -f tmp')
    os.system('mkdir -p "%s"' % name)

    if 'name' in conf:
        if isinstance(conf['name'], dict):
            name += '/' + select(soup, conf['name'], select_one=True)
        else:
            name += '/' + conf['name']

    for item in select(soup, conf['item']):
        if item.startswith('//'):
            full_url = protocol + ':' + item
        elif item.startswith('/'):
            full_url = protocol + '://' + domain_name + item
        else:
            full_url = item
        if download:
            os.system('wget %s "%s" -P "%s"' % (wget_extra_args, full_url, name))
        if 'follow' in conf:
            process_page(conf['follow'], name, address=full_url)
        if 'recurse-condition-regex' in conf:
            pattern = re.compile(conf['recurse-condition-regex'])
            if pattern.match(full_url) is None:
                process_page(conf['recurse-final'], name, address=full_url)
            else:
                process_page(conf, name, address=full_url)


def main():
    conf = read_conf(sys.argv[1])
    for page in conf:
        process_page(conf[page])
