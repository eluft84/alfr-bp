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

    # Retrieve posts from cache if available and no more than 600
    # seconds old

    def wrapper():
        """`cached_data` can only take a bare callable (no args),
        so we need to wrap callables needing arguments in a function
        that needs none.
        """
        return get_people(wf, query)

    wf.cached_data('sametimechat-person', wrapper, max_age=2)


if __name__ == '__main__':
    wf = Workflow3()
    wf.logger.setLevel(logging.DEBUG)
    wf.run(main)
