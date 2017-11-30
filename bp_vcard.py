#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
import urllib
import vobject
import tempfile
import base64
import requests
import re
import subprocess

from workflow import Workflow, web, ICON_INFO

log = None


def clean_number(nbr, plus=False):
    out = nbr.replace(' ', '')
    out = out.replace('-', '')
    out = out.replace(',', '')
    out = out.strip()

    out = re.sub(r'\([^)]*\)', '', out)

    if plus:
        return '+' + out
    else:
        return '00' + out


def main(wf):
    # https://w3-services1.w3-969.ibm.com/myw3/unified-profile/v1/docs/instances/master?userId=6D9518897&_=1511950277764

    item = json.loads(os.environ['item'])

    url = \
        'https://w3-services1.w3-969.ibm.com/myw3/unified-profile/v1/docs/instances/master?userId=' \
        + item['uid'] + '&_=1511950277764'
    r = web.get(url).json()

    j = vobject.vCard()
    j.add('n')
    j.n.value = vobject.vcard.Name(family=r['content']['identity_info'
                                   ]['name']['last'], given=r['content'
                                   ]['identity_info']['name']['first'])

    j.add('fn')
    j.fn.value = item['nameFull']

    j.add('email')
    j.email.value = item['preferredIdentity'].lower()
    j.email.type_param = 'INTERNET'

    j.add('org')
    j.org.value = ['IBM']

    if item.get('role'):
        j.add('title')
        j.title.value = item['role']

    if item.get("telephone_mobile"):
        j.add('tel')
        j.tel.type_param = 'MOBILE'
        j.tel.value = clean_number(item['telephone_mobile'], True)

    if item.get("telephone_office"):
        j.add('tel')
        j.contents['tel'][len(j.contents['tel'])-1].type_param='WORK'
        j.contents['tel'][len(j.contents['tel'])-1].value=clean_number(item['telephone_office'], True)

    #t = r['content']['identity_info']['address']['business']
    #j.add('address')
    #j.address.type_param='WORK'
    #adr = vobject.vcard.Address(street=t['address'][0], city=t['locality'], code=t['zip'], country=t['country'], region = (t['state'] if t.get('state') else ''));
    #adr = vobject.vcard.Address(t['address'][0], t['locality'], (t['state'] if t.get('state') else ''), t['zip'], t['country'])
    #j.address.value = adr

    try:
        url = \
            'https://w3-services1.w3-969.ibm.com/myw3/unified-profile-photo/v1/image/' \
            + item['uid'] + '?def=null&type=bp'
        jpg = tempfile.NamedTemporaryFile(delete=False)
        urllib.urlretrieve(url, jpg.name)
        if os.stat(jpg.name).st_size > 0:
            j.add('photo')
            j.photo.encoding_param = 'b'
            j.photo.type_param = 'JPEG'
            photo_fh = open(jpg.name, 'rb')
            j.photo.value = photo_fh.read()
            photo_fh.close()
    except:
        pass

    with tempfile.NamedTemporaryFile(suffix='.vcf', delete=False) as \
        temp:
        temp.write(j.serialize())
        subprocess.Popen(["open", "-a","Contacts",
                  temp.name])


if __name__ == '__main__':

    # Create a global `Workflow` object

    wf = Workflow(update_settings={'github_slug': 'nidayand/alfr-bp',
                  'frequency': 1})  # Your username and the workflow's repo's name
                                    # Optional number of days between checks for updates
    log = wf.logger

    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.

    sys.exit(wf.run(main))

