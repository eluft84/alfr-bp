#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json

from workflow import Workflow3

log = None


def add_item( wf, atitle, asubtitle, aquery, aaction, aicon=None, aenabled=True):
    arg = {'alfredworkflow': {'arg': aquery,
           'variables': {'action': aaction}}}
    wf.add_item(title=atitle, subtitle=asubtitle, arg=json.dumps(arg),
                valid=aenabled, icon=(aicon if aicon else ''))

default_order = order = ['profile', 'verse', 'sametimechat', 'sametimesut', 'facetime', 'messages', 'whatsapp', 'pushbullet', 'ciscospark', 'copy', 'paste', 'save']
def getorder():
    if wf.stored_data('bp-order'):
        order = wf.stored_data('bp-order')

        # Verify that there are no options missing in order list
        for a in default_order:
            if a not in order:
                order.append(a)
                wf.store_data('bp-order', order)
        return order
    else:
        wf.store_data('bp-order', default_order)
        return default_order


def main(wf):

    order = getorder()

    for i in order:
        if order.index(i) == 0:
            enabled = False
        else:
            enabled = True

        moveup = 'Move up' if order.index(i) > 0 else ''

        if i == 'profile':
            add_item(wf, 'Profile', moveup, '', 'profile', 'images/profile.png', enabled)
        elif i == 'verse':
            add_item(wf, 'Verse', moveup, '', 'verse', 'images/verse.png', enabled)
        elif i == 'sametimechat':
            add_item(wf, 'Sametime Chat', moveup, '', 'sametimechat', 'images/st.png', enabled)
        elif i == 'sametimesut':
            add_item(wf, 'Sametime Unified Telephony', moveup, '','sametimesut', 'images/mobile.png', enabled)
        elif i == 'facetime':
            add_item(wf, 'FaceTime',moveup, '', 'facetime', 'images/facetime.png', enabled)
        elif i == 'messages':
            add_item(wf, 'Messages', moveup, '', 'messages', 'images/imessage.png', enabled)
        elif i == 'whatsapp':
            add_item(wf, 'WhatsApp', moveup, '', 'whatsapp', 'images/whatsapp.png', enabled)
        elif i == 'pushbullet':
            add_item(wf, 'Pushbullet', moveup, '', 'pushbullet', 'images/pushbullet.png', enabled)
        elif i == 'ciscospark':
            add_item(wf, 'Cisco Spark', moveup, '', 'ciscospark', 'images/ciscospark.png', enabled)
        elif i == 'copy':
            add_item(wf, 'Copy to clipboard', moveup, '', 'copy', 'images/clipboard.png', enabled)
        elif i == 'paste':
            add_item(wf, 'Paste to front most app', moveup, '', 'paste', 'images/paste.png', enabled)
        elif i == 'save':
            add_item(wf, 'Save', moveup, '', 'save', 'images/contacts.png', enabled)

    wf.send_feedback()


if __name__ == '__main__':

    # Create a global `Workflow` object

    wf = Workflow3()

    log = wf.logger

    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.

    sys.exit(wf.run(main))
