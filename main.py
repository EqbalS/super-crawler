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
        value = get_value(element, conf)
        if 'regex-exclude' in conf:
            pattern = re.compile(conf['regex-exclude'])
            if pattern.match(value) is not None:
                continue
        if 'regex-filter' in conf:
            pattern = re.compile(conf['regex-filter'])
            if pattern.match(value) is None:
                continue
        values.append(value)
    return values


def get_full_url(address, item, domain_name, protocol):
    if item.startswith('//'):
        return protocol + ':' + item
    if item.startswith('/'):
        return protocol + '://' + domain_name + item
    if item.startswith('http://') or item.startswith('https://'):
        return item
    else:
        if not address.endswith('/'):
            address += '/'
        return address + item


def do_action(conf, name, wget_extra_args, address, item, domain_name, protocol):
    if 'download' in conf and conf['download']:
        full_url = get_full_url(address, item, domain_name, protocol)
        print 'Downloading %s -> %s' % (full_url, name)
        os.system('wget %s "%s" -P "%s" 2> /dev/null' % (wget_extra_args, full_url, name))
    if 'print' in conf and conf['print']:
        print item
    if 'follow' in conf:
        process_page(conf['follow'], name, address=get_full_url(address, item, domain_name, protocol))
    if 'recurse-condition-regex' in conf:
        full_url = get_full_url(address, item, domain_name, protocol)
        pattern = re.compile(conf['recurse-condition-regex'])
        if pattern.match(full_url) is None:
            do_action(conf['recurse-final'], name, wget_extra_args, address, item, domain_name, protocol)
        else:
            process_page(conf, name, address=full_url)


def process_page(conf, name='.', address=None):
    if address is None:
        address = conf['address']
    wget_extra_args = ''
    if 'wget-extra-args' in conf:
        wget_extra_args = conf['wget-extra-args']

    domain_name, protocol = find_domain_name(address)
    print 'Getting %s' % address
    os.system('wget %s "%s" -O tmp 2> /dev/null' % (wget_extra_args, address))
    soup = BeautifulSoup(open('tmp').read(), 'html.parser')
    os.system('rm -f tmp')
    os.system('mkdir -p "%s"' % name)

    if 'name' in conf:
        if isinstance(conf['name'], dict):
            name += '/' + select(soup, conf['name'], select_one=True)
        else:
            name += '/' + conf['name']

    for item in select(soup, conf['item']):
        do_action(conf, name, wget_extra_args, address, item, domain_name, protocol)


def main():
    conf = read_conf(sys.argv[1])
    for page in conf:
        process_page(conf[page])
