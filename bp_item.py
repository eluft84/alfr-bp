#!/usr/bin/python
# encoding: utf-8

import sys
import os
import json
import copy
import urllib
import re
import urllib2
import time
import ciscosparkapi
from workflow import Workflow3, web
from workflow.background import run_in_background, is_running
from datetime import tzinfo, timedelta, datetime
import dateutil.parser

log = None
ZERO = timedelta(0)

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


class UTC(tzinfo):
	def utcoffset(self, dt):
		return ZERO
	def tzname(self, dt):
		return "UTC"
	def dst(self, dt):
		return ZERO

def get_thumbnail(uid):
	filename = wf.datadir + '/cached/{0}.jpg'.format(uid)
	if thumbnail_cache_exists(uid) is True:
		return filename
	else:
		# Try to get a copy
		try:
			img = urllib2.urlopen('https://w3-services1.w3-969.ibm.com/myw3/unified-profile-photo/v1/image/{0}?def=blue&s=64'.format(uid))
			localFile = open(filename, 'wb')
			localFile.write(img.read())
			localFile.close()
			return filename
		except:
			return wf.workflowdir+"/icon.png"
			pass

def thumbnail_cache_exists(uid):
	filename = wf.datadir + '/cached/{0}.jpg'.format(uid)
	if os.path.isfile(filename):
		days_old = (time.time() - os.stat(filename).st_mtime) / 86400
		if days_old > 7:
			return False
		else:
			return True
	return False

def add_item(wf, atitle, asubtitle, aquery, aaction, aicon = None, avalid=True):
	arg = {"alfredworkflow": {"arg": aquery,"variables": {"action": aaction}}}
	wf.add_item(title=atitle, subtitle=asubtitle, arg=json.dumps(arg), valid=avalid, icon=(aicon if aicon else ""))

def clean_number(nbr, plus = False, withoutzero = False):
	out = nbr.replace(" ", "")
	out = out.replace("-", "")
	out = out.replace(",", "")
	out = out.replace('.', '')
	out = out.strip()

	out = re.sub(r'\([^)]*\)', '', out)
	#print result

	if plus:
		return "+"+out
	elif withoutzero:
		return out
	else:
		return "00"+out

def add_person(wf, item):
	if is_running('update-outofoffice'):
		add_item(wf, 'Show profile of '+item["nameFull"], 'Open in default browser', "http://w3.ibm.com/bluepages/profile.html?uid="+item["uid"], "browser", get_thumbnail(item["uid"]))
		wf.rerun = 1
	else:
		r = wf.stored_data('outofoffice-person')
		add_item(wf, 'Show profile of '+item["nameFull"]+ (' (out of office)' if r['enabled'] else '') , 'Open in default browser', "http://w3.ibm.com/bluepages/profile.html?uid="+item["uid"], "browser", get_thumbnail(item["uid"]))


def add_mail(wf,item):
	add_item(wf, 'Send mail to '+item["preferredIdentity"].lower(), 'Open IBM Verse', "https://mail.notes.na.collabserv.com/verse?mode=compose#href=mailto%3A"+urllib.quote(item["preferredIdentity"].lower()), "browser", "images/verse.png")

def add_sametimechat(wf, item):
	if is_running('update-sametimechat'):
		add_item(wf, 'Checking status','Using Sametime chat',None,None,'images/st.png', False)
		wf.rerun = 1
	else:
		r = wf.stored_data('sametimechat-person')
		# Add chat
		if r["status"]>0:
			add_item(wf, 'Chat with '+item["nameFull"], 'Status: '+r["statusMessage"], "http://localhost:59449/stwebapi/chat?userId="+urllib.quote(item["preferredIdentity"]), "urlcall", "images/st.png")
		else:
			add_item(wf, 'Not available','Using Sametime chat',None,None,'images/st.png', False)

def add_sametimesut(wf, item, hideoffice):
	try:
		web.get('http://localhost:59449/stwebapi/call')

		if item.get("telephone_mobile"):
			add_item(wf, 'Call mobile: +'+item["telephone_mobile"], 'Using Sametime Unified Telephony', "http://localhost:59449/stwebapi/call?number="+urllib.quote(clean_number(item["telephone_mobile"])), "urlcall", "images/mobile.png")

		if item.get("telephone_office") and not hideoffice or not item.get("telephone_mobile"):
			add_item(wf, 'Call office: +'+item["telephone_office"], 'Using Sametime Unified Telephony', "http://localhost:59449/stwebapi/call?number="+urllib.quote(clean_number(item["telephone_office"])), "urlcall", "images/office.png")
	except:
		pass

def add_facetime(wf, item, hideoffice):
	if item.get("telephone_mobile"):
		add_item(wf, 'Call mobile: +'+item["telephone_mobile"], 'Using FaceTime', clean_number(item["telephone_mobile"], True), "facetime", "images/facetime.png")

	if item.get("telephone_office") and not hideoffice or not item.get("telephone_mobile"):
		add_item(wf, 'Call office: +'+item["telephone_office"], 'Using FaceTime', clean_number(item["telephone_office"], True), "facetime", "images/facetime.png")


def add_pushbullet(wf,item):
	if item.get("telephone_mobile"):
		add_item(wf, 'Text mobile: +'+item["telephone_mobile"], 'Using Pushbullet', clean_number(item["telephone_mobile"], True), "pushbullet", "images/pushbullet.png")

def add_imessage(wf, item):
	if item.get("telephone_mobile"):
		add_item(wf, 'Text mobile: +'+item["telephone_mobile"], 'Using Messages', clean_number(item["telephone_mobile"], True), "imessage", "images/imessage.png")

def add_whatsapp(wf,item):
	if item.get("telephone_mobile"):
		add_item(wf, 'Chat with '+item["nameFull"], 'Using WhatsApp', "https://web.whatsapp.com/send?phone="+urllib.quote(clean_number(item["telephone_mobile"], False, True)), "browser", "images/whatsapp.png")

def add_cisco(wf, item):
	if is_running('update-cisco'):
		add_item(wf, 'Checking status','Using Cisco Spark',item["preferredIdentity"].lower(),'ciscospark','images/ciscospark.png', False)
		wf.rerun = 1
	else:
		cisco_person = wf.stored_data('cisco-person')
		cisco_person = ciscosparkapi.Person(cisco_person)
		if not cisco_person.status in ['unknown','pending']:
			# Get time
			lastActivity = dateutil.parser.parse(cisco_person.lastActivity)
			now = datetime.now(UTC())
			d = datetime(1,1,1) + (now - lastActivity)
			txt = 'Active '
			if (d.day-1) > 1:
				txt += str(d.day-1) + ' days ago'
			elif (d.day-1) > 0:
				txt += str(d.day-1) + ' day ago'
			elif d.hour > 1:
				txt += str(d.hour) + ' hours ago'
			elif d.hour > 0:
				txt += str(d.hour) + ' hour ago'
			elif d.minute > 1:
				txt += str(d.minute) + ' minutes ago'
			elif d.minute > 0:
				txt += str(d.minute) + ' minute ago'

			add_item(wf, 'Chat with '+item["nameFull"],'Using Cisco Spark ('+txt+')',item["preferredIdentity"].lower(),'ciscospark','images/ciscospark.png')
		else:
			add_item(wf, 'Not available','Using Cisco Spark',item["preferredIdentity"].lower(),'ciscospark','images/ciscospark.png', False)


def main(wf):
	item = json.loads(os.environ['item'])

	# This is set in bp_search initially and firsttime param
	# is used for the refresh functions
	firsttime = False
	if wf.stored_data('first-time'):
		firsttime = True
		wf.clear_data(lambda f: f.endswith('first-time.cpickle'))


	# Add timestamp to item if it doesn't exist
	try:
		item["added_timestamp"]
	except:
		item["added_timestamp"] = time.time()

	# Add item to store
	items = wf.stored_data('items')
	if items:
		#Check if it already exists and if so remove
		foundIndex = -1
		for index in range(len(items)):
			if items[index]["uid"] == item["uid"]:
				foundIndex = index
				break
		if foundIndex > -1:
			items.pop(foundIndex)

	else:
		items = []
	items.insert(0,item)
	if len(items)>100:
		items.pop()
	wf.store_data('items',items, serializer='json')

	# Initializing params
	phone_duplicates = False
	imessage = False
	sut = True
	facetime = False
	pushbullet = False
	whatsapp = False
	sametimechat = True
	hideoffice = False

	# Check out of office
	if firsttime:
		run_in_background('update-outofoffice', ['/usr/bin/python', wf.workflowfile('bp_bg_outofoffice.py'),item['uid']])

	# Sametime
	if wf.stored_data('bp-sametimechat'):
		sametimechat = wf.stored_data('bp-sametimechat').lower().strip() in ("yes", "true", "1", "on", "yeah")
		if sametimechat and firsttime:
			run_in_background('update-sametimechat', ['/usr/bin/python', wf.workflowfile('bp_bg_sametimechat.py'),item['preferredIdentity']])

	#iPhone
	if wf.stored_data('bp-imessage'):
		imessage = wf.stored_data('bp-imessage').lower().strip() in ("yes", "true", "1", "on", "yeah")

	#WhatsApp
	if wf.stored_data('bp-whatsapp'):
		whatsapp = wf.stored_data('bp-whatsapp').lower().strip() in ("yes", "true", "1", "on", "yeah")

	#Sametime Unified Telephony
	if wf.stored_data('bp-sut'):
		sut = wf.stored_data('bp-sut').lower().strip() in ('yes', 'true', '1', 'on', 'yeah')

	#FaceTime
	if wf.stored_data('bp-facetime'):
		facetime = wf.stored_data('bp-facetime').lower().strip() \
			in ('yes', 'true', '1', 'on', 'yeah')

	#Pushbullet
	if wf.stored_data('bp-device') and wf.stored_data('bp-api'):
		pushbullet = True

	#Hide office
	if wf.stored_data('bp-officephone'):
		hideoffice = wf.stored_data('bp-officephone').lower().strip() in ('yes', 'true', '1', 'on', 'yeah')

	# Cisco Spark
	cisco = False
	if wf.stored_data('bp-cisco'):
		cisco = True
		if firsttime:
			run_in_background('update-cisco', ['/usr/bin/python', wf.workflowfile('bp_bg_cisco.py'),item['preferredIdentity']])


	# Check if the office and mobile are the same number
	if item.get("telephone_mobile") and item.get("telephone_office") and (clean_number(item.get("telephone_mobile")) == clean_number(item.get("telephone_office"))):
		# Remove office phone if mobile is the same
		del item["telephone_office"]

	# CREATE THE ORDERED LIST
	order = getorder()

	for i in order:
		if i == 'profile':
			add_person(wf, item)

		elif i == 'sametimechat':
			# Sametime chat
			if sametimechat:
				add_sametimechat(wf,item)

		elif i == 'sametimesut':
			# Sametime SUT
			if sut:
				add_sametimesut(wf, item, hideoffice)

		elif i == 'facetime':
			# FaceTime
			if facetime:
				add_facetime(wf, item, hideoffice)

		elif i == 'messages':
			#iPhone SMS
			if imessage:
				add_imessage(wf,item)

		elif i == 'whatsapp':
			#WhatsApp
			if whatsapp:
				add_whatsapp(wf,item)

		elif i == 'pushbullet':
			#Pushbullet
			if pushbullet:
				add_pushbullet(wf, item)

		elif i == 'ciscospark':
			#Cisco Spark
			if cisco:
				add_cisco(wf,item)

		elif i == 'copy':
			# Add copy email to clipboard
			add_item(wf, 'Copy '+item["preferredIdentity"].lower(), 'To clipboard', item["preferredIdentity"].lower(), "clipboard", "images/clipboard.png")

			# Add copy mobile to clipboard
			if item.get("telephone_mobile"):
				add_item(wf, 'Copy mobile: +'+item["telephone_mobile"], 'To clipboard', clean_number(item["telephone_mobile"], True), "clipboard", "images/clipboard.png")

			# Add copy office to clipboard
			if item.get("telephone_office") and not hideoffice or not item.get("telephone_mobile") and item.get("telephone_office"):
				add_item(wf, 'Copy office: +'+item["telephone_office"], 'To clipboard', clean_number(item["telephone_office"], True), "clipboard", "images/clipboard.png")

		elif i == 'paste':
			# Add copy email and paste
			add_item(wf, 'Paste '+item["preferredIdentity"].lower(), 'To the front most app and copy to clipboard', item["preferredIdentity"].lower(), "paste", "images/paste.png")

		elif i == 'save':
			add_item(wf, "Save", "Store profile in Contacts", "","save", "images/contacts.png")

		elif i == 'verse':
			# Add mail
			add_mail(wf,item)

	# Send output to Alfred. You can only call this once.
	# Well, you *can* call it multiple times, but Alfred won't be listening	# any more...
	wf.send_feedback()


if __name__ == '__main__':
	# Create a global `Workflow` object
	wf = Workflow3()
	log = wf.logger
	# Call your entry function via `Workflow.run()` to enable its helper
	# functions, like exception catching, ARGV normalization, magic
	# arguments etc.
	sys.exit(wf.run(main))
