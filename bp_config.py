#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import json
import urllib

from workflow import Workflow, web, ICON_INFO

log = None


def add_item(
    wf,
    atitle,
    asubtitle,
    aquery,
    aaction,
    aicon=None,
    aenabled=True
    ):

    arg = {'alfredworkflow': {'arg': aquery,
           'variables': {'action': aaction}}}
    wf.add_item(title=atitle, subtitle=asubtitle, arg=json.dumps(arg),
                valid=aenabled, icon=(aicon if aicon else ''))


def main(wf):

    args = wf.args

    query = args[0]

    # Initializing params

    imessage = False
    facetime = False
    sut = True
    pushbullet = False
    ciscospark = False
    whatsapp = False

    # Check status
    if wf.stored_data('bp-imessage'):
        imessage = wf.stored_data('bp-imessage').lower().strip() \
            in ('yes', 'true', '1', 'on', 'yeah')
    if wf.stored_data('bp-facetime'):
        facetime = wf.stored_data('bp-facetime').lower().strip() \
            in ('yes', 'true', '1', 'on', 'yeah')
    if wf.stored_data('bp-cisco'):
        ciscospark = True
    if wf.stored_data('bp-whatsapp'):
        whatsapp = wf.stored_data('bp-whatsapp').lower().strip() \
            in ('yes', 'true', '1', 'on', 'yeah')

    if wf.stored_data('bp-device') and wf.stored_data('bp-api'):
        pushbullet = True
    if wf.stored_data('bp-sut'):
        sut = wf.stored_data('bp-sut').lower().strip() \
            in ('yes', 'true', '1', 'on', 'yeah')

    add_item(wf, 'Sametime Unified Telephony '+('ENABLED' if sut else 'DISABLED'), 'Toggle SUT (call with Sametime)', ''
             , 'sametime','images/mobile.png')
    add_item(wf, 'FaceTime '+('ENABLED' if facetime else 'DISABLED'),
             'Toggle FaceTime integration (call using iPhone)', '',
             'facetime','images/facetime.png')
    add_item(wf, 'Messages '+('ENABLED' if imessage else 'DISABLED'),
             'Toggle Messages integration (SMS using iPhone)', '',
             'imessage','images/imessage.png')
    add_item(wf, 'WhatsApp '+('ENABLED' if whatsapp else 'DISABLED'),
             'Toggle WhatsApp integration (links to web-UI)', '',
             'whatsapp','images/whatsapp.png')
    add_item(wf, 'Pushbullet '+('ENABLED' if pushbullet else 'DISABLED'),
             'Toggle Pushbullet integration (SMS using Android)', '',
             'pushbullet','images/pushbullet.png')
    add_item(wf, 'Cisco Spark '+('ENABLED' if ciscospark else 'DISABLED'),
             'Toggle Cisco Spark integration (messages)', '',
             'ciscospark','images/ciscospark.png')
    add_item(wf, 'Link to Mac@IBM forum',
             'Ask questions or report bugs', 'https://w3-connections.ibm.com/forums/html/topic?id=efeae0bf-3d7e-48a2-8573-b31f940c111b',
             'url')
    add_item(wf, 'Current version: '+'{0}'.format(wf.version),
             'Goto Github releases', 'https://github.com/nidayand/alfr-bp/releases',
             'url')

    wf.send_feedback()


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
