#!/usr/bin/python
# encoding: utf-8

import sys
import os
import json
import urllib
import urllib2
import time

from workflow import Workflow, web, ICON_INFO, ICON_ERROR,ICON_NOTE

log = None

def get_thumbnail(uid):
    filename = wf.datadir + '/cached/{0}.jpg'.format(uid)
    if thumbnail_cache_exists(uid) is True:
        return filename
    else:
        return wf.workflowdir+"/icon.png"

def thumbnail_cache_exists(uid):
    filename = wf.datadir + '/cached/{0}.jpg'.format(uid)
    if os.path.isfile(filename):
        days_old = (time.time() - os.stat(filename).st_mtime) / 86400
        if days_old > 7:
            return False
        else:
            return True
    return False

def key_for_item(item):
    return '{} {}'.format(item['notesEmailWithDomain'],item['preferredIdentity'])

def main(wf):
    # https://github.com/deanishe/alfred-workflow
    # http://www.deanishe.net/alfred-workflow/
    args = wf.args

    query = args[0]

    counter = 0

    #If there is an update prompt for updating action
    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version available', 'Action this item to install the update', autocomplete='workflow:update', icon=ICON_INFO)


    # If there is no argument passed take last used from cache (if there is a cache)
    uidhitlist = []
    if len(query.strip()) == 0:
        try:
            items = wf.stored_data('items')
            if items and len(items)>0:
                hcount = 0
                for item in items:
                    wf.add_item(title=item["nameFull"], subtitle=(item["role"] if item.get("role") else ""), autocomplete=item["nameFull"], arg=json.dumps(item), valid=True, quicklookurl=("http://w3.ibm.com/bluepages/profile.html?uid="+item["uid"]), icon=get_thumbnail(item["uid"]))
                    counter+=1

                    #Show max 9 from cache
                    hcount = hcount +1
                    if hcount == 9:
                        break
        except:
            #delete json
            wf.clear_data(lambda f: f.endswith('items.json'))
            pass

    ## First check store
    else:
        try:
            items = wf.stored_data('items')
            if items:
                hits = wf.filter(query, items, key_for_item, min_score=20)
                log.debug(hits)
                hcount = 0
                for hit in hits:
                    wf.add_item(title=hit["nameFull"], subtitle=(hit["role"] if hit.get("role") else ""), autocomplete=hit["nameFull"], arg=json.dumps(hit), valid=True, quicklookurl=("http://w3.ibm.com/bluepages/profile.html?uid="+hit["uid"]), icon=get_thumbnail(hit["uid"]))
                    #Add UID to hit list to avoid double entries
                    uidhitlist.append(hit["uid"])
                    counter+=1

                    #Show max 5 from cache
                    hcount = hcount +1
                    if hcount == 5:
                        break
        except:
            #do nothing
            pass

    try:
        if len(query)>0:
            url = "https://w3-services1.w3-969.ibm.com/myw3/unified-profile/v1/search/user?searchConfig=optimized_search&rows=20&timeout=2000&query="+urllib.quote(query.encode("utf-8"))
            log.debug("Calling: "+url)
            r = web.get(url).json()

            for item in r["results"]:
                #Only add if UID not is in the cached hit list and it has an email
                if item["uid"] not in uidhitlist and item.get("preferredIdentity") and "FUNCTIONAL-ID" not in item["nameFull"]:
                    wf.add_item(title=item["nameFull"], subtitle=(item["role"] if item.get("role") else ""), autocomplete=item["nameFull"], arg=json.dumps(item), valid=True, quicklookurl=("http://w3.ibm.com/bluepages/profile.html?uid="+item["uid"]), icon=get_thumbnail(item["uid"]))
                    counter+=1
    except:
        wf.add_item(title="Unable to reach Bluepages", subtitle="Please verify that you are connected to the IBM Intranet", valid=False, icon=ICON_ERROR)
        pass


    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but Alfred won't be listening	# any more...
    if counter == 0:
        wf.add_item(title="No hits in Bluepages", subtitle="Add or adjust your search parameter", valid=False, icon=ICON_NOTE)

    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    wf = Workflow(update_settings={
            # Your username and the workflow's repo's name
            'github_slug': 'nidayand/alfr-bp',

            # Optional number of days between checks for updates
            'frequency': 1
    })
    log = wf.logger

    # Create folder if not available
    filename = wf.datadir + '/cached/0.jpg'
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    # Delete old cached images > 7 days
    path = wf.datadir + '/cached/'
    for f in os.listdir(path):
        if os.stat(os.path.join(path,f)).st_mtime < time.time() - 7 * 86400:
            if os.path.isfile(os.path.join(path, f)):
                os.remove(os.path.join(path, f))

    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
    sys.exit(wf.run(main))
