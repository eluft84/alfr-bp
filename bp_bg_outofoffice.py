# encoding: utf-8

from workflow import Workflow3,web
import urllib
import logging


def get_people(wf, uid):
    headers = {'X-Up-Token': 'up-0b4f321bf090fcf3792f5fffc4fcd1801fab37e0470c66d46cb0f0181b316a7'}
    try:
        r = web.get("https://w3-services1.w3-969.ibm.com/myw3/unified-profile/v2/ooo/uid/"+uid, headers=headers, timeout=5)
        return r.json()
    except:
        return '{"enabled": false}'


def main(wf):
    args = wf.args
    query = args[0]

    # Retrieve posts from cache if available and no more than 600
    # seconds old

    val = get_people(wf, query)

    wf.store_data('outofoffice-person', val, serializer='json')


if __name__ == '__main__':
    wf = Workflow3()
    wf.logger.setLevel(logging.DEBUG)
    wf.run(main)
