# encoding: utf-8

from workflow import Workflow3
from ciscosparkapi import CiscoSparkAPI
import ciscosparkapi
import logging
from time import sleep


def get_people(wf, email):
    cisco = CiscoSparkAPI(access_token=wf.stored_data('bp-cisco'))
    list_people = cisco.people.list(email=email)
    for person in list_people:
        # Returning the found person at cisco
        return person.to_json()
    # Creating a fake person
    return ciscosparkapi.Person('{"status": "unknown", "displayName": "NA", "created": "2017-11-23T19:29:17.339Z", "type": "person", "emails": ["na@ibm.com"], "lastActivity": "2018-02-23T09:04:09.732Z", "orgId": "", "avatar": "", "nickName": "N/A", "id": "1"}').to_json()


def main(wf):
    args = wf.args
    query = args[0]

    # Retrieve posts from cache if available and no more than 600
    # seconds old

    def wrapper():
        """`cached_data` can only take a bare callable (no args),
        so we need to wrap callables needing arguments in a function
        that needs none.
        """
        return get_people(wf, query)

    wf.cached_data('cisco-person', wrapper, max_age=2)


if __name__ == '__main__':
    wf = Workflow3()
    wf.logger.setLevel(logging.DEBUG)
    wf.run(main)