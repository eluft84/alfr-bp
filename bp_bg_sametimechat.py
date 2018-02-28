# encoding: utf-8

from workflow import Workflow3,web
import urllib
import logging


def get_people(wf, email):
    try:
        r = web.get("http://localhost:59449/stwebapi/getstatus?userId="+urllib.quote(email), timeout=5)
        return r.json()
    except:
        return '{"status":0}'


def main(wf):
    args = wf.args
    query = args[0]

    val = get_people(wf, query)

    wf.store_data('sametimechat-person', val, serializer='json')


if __name__ == '__main__':
    wf = Workflow3()
    wf.logger.setLevel(logging.DEBUG)
    wf.run(main)
