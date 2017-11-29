#!/usr/bin/python
# encoding: utf-8

import sys
import os
import json
import copy
import urllib
import re

from workflow import Workflow, web

def add_item(wf, atitle, asubtitle, aquery, aaction, aicon = None):
	arg = {"alfredworkflow": {"arg": aquery,"variables": {"action": aaction}}}
	wf.add_item(title=atitle, subtitle=asubtitle, arg=json.dumps(arg), valid='True', icon=(aicon if aicon else ""))

def clean_number(nbr, plus = False):
	out = nbr.replace(" ", "")
	out = out.replace("-", "")
	out = out.replace(",", "")
	out = out.strip()

	out = re.sub(r'\([^)]*\)', '', out)
	#print result

	if plus:
		return "+"+out
	else:
		return "00"+out



def main(wf):
	# https://github.com/deanishe/alfred-workflow
	# http://www.deanishe.net/alfred-workflow/
	args = wf.args

	item = json.loads(os.environ['item'])

	#Add item to store
	items = wf.stored_data('items')
	if items:
		#Check if it already exists and if so remove
		#items = json.loads(items)
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

	# Add profile
	add_item(wf, 'Show profile of '+item["nameFull"], 'Open in default browser', "http://w3.ibm.com/bluepages/profile.html?uid="+item["uid"], "browser")

	# Add mail
	add_item(wf, 'Send mail to '+item["preferredIdentity"].lower(), 'Open IBM Verse', "https://mail.notes.na.collabserv.com/verse?mode=compose#href=mailto%3A"+urllib.quote(item["preferredIdentity"]), "browser", "images/verse.png")

	# Initializing params
	phone_duplicates = False
	imessage = False

	#iPhone
	if wf.stored_data('bp-imessage'):
		imessage = wf.stored_data('bp-imessage').lower().strip() in ("yes", "true", "1", "on", "yeah")

	try:
		try:
			r = web.get("http://localhost:59449/stwebapi/getstatus?userId="+urllib.quote(item["preferredIdentity"]), timeout=5)
			r = r.json()

			# Add chat
			if r["status"]>0:
				add_item(wf, 'Chat with '+item["nameFull"], 'Status: '+r["statusMessage"], "http://localhost:59449/stwebapi/chat?userId="+urllib.quote(item["preferredIdentity"]), "urlcall", "images/st.png")
		except:
			pass

		r = web.get('http://localhost:59449/stwebapi/call')

		#Check if the office and mobile are the same number
		if item.get("telephone_mobile") and item.get("telephone_office") and (clean_number(item.get("telephone_mobile")) == clean_number(item.get("telephone_office"))):
			phone_duplicates = True
		else:
			phone_duplicates = False

		if item.get("telephone_mobile"):
			add_item(wf, 'Call mobile: +'+item["telephone_mobile"], 'Using Sametime Unified Telephony', "http://localhost:59449/stwebapi/call?number="+urllib.quote(clean_number(item["telephone_mobile"])), "urlcall", "images/mobile.png")
			if imessage:
				add_item(wf, 'Call mobile: +'+item["telephone_mobile"], 'Using FaceTime', clean_number(item["telephone_mobile"], True), "facetime", "images/facetime.png")

		if item.get("telephone_office") and  not phone_duplicates:
			add_item(wf, 'Call office: +'+item["telephone_office"], 'Using Sametime Unified Telephony', "http://localhost:59449/stwebapi/call?number="+urllib.quote(clean_number(item["telephone_office"])), "urlcall", "images/office.png")
			if imessage:
				add_item(wf, 'Call mobile: +'+item["telephone_office"], 'Using FaceTime', clean_number(item["telephone_office"], True), "facetime", "images/facetime.png")
	except:
		pass

	#Pushbullet
	if wf.stored_data('bp-device') and wf.stored_data('bp-api'):
		if item.get("telephone_mobile"):
			add_item(wf, 'Text mobile: +'+item["telephone_mobile"], 'Using Pushbullet', clean_number(item["telephone_mobile"], True), "pushbullet", "images/pushbullet.png")
		if item.get("telephone_office") and not phone_duplicates:
			add_item(wf, 'Text office: +'+item["telephone_office"], 'Using Pushbullet', clean_number(item["telephone_office"], True), "pushbullet", "images/pushbullet.png")

	#iPhone SMS
	if imessage:
		if item.get("telephone_mobile"):
			add_item(wf, 'Text mobile: +'+item["telephone_mobile"], 'Using Messages', clean_number(item["telephone_mobile"], True), "imessage", "images/imessage.png")
		if item.get("telephone_office") and not phone_duplicates:
			add_item(wf, 'Text office: +'+item["telephone_office"], 'Using Messages', clean_number(item["telephone_office"], True), "imessage", "images/imessage.png")

	# Add copy email and paste
	add_item(wf, 'Paste '+item["preferredIdentity"].lower(), 'To the front most app and copy to clipboard', item["preferredIdentity"].lower(), "paste", "images/paste.png")

	# Add copy email to clipboard
	add_item(wf, 'Copy '+item["preferredIdentity"].lower(), 'To clipboard', item["preferredIdentity"], "clipboard", "images/clipboard.png")

	# Add copy mobile to clipboard
	try:
		if item.get("telephone_mobile"):
			add_item(wf, 'Copy mobile: +'+item["telephone_mobile"], 'To clipboard', clean_number(item["telephone_mobile"], True), "clipboard", "images/clipboard.png")
	except:
		pass
	# Add copy office to clipboard
	try:
		if item.get("telephone_office") and not phone_duplicates:
			add_item(wf, 'Copy office: +'+item["telephone_office"], 'To clipboard', clean_number(item["telephone_office"], True), "clipboard", "images/clipboard.png")
	except:
		pass

	add_item(wf, "Save", "Store profile in Contacts", "","save", "images/contacts.png")


	# Send output to Alfred. You can only call this once.
	# Well, you *can* call it multiple times, but Alfred won't be listening	# any more...
	wf.send_feedback()


if __name__ == '__main__':
	# Create a global `Workflow` object
	wf = Workflow()
	# Call your entry function via `Workflow.run()` to enable its helper
	# functions, like exception catching, ARGV normalization, magic
	# arguments etc.
	sys.exit(wf.run(main))
