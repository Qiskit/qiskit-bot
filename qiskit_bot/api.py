# This code is part of Qiskit.
#
# (C) Copyright IBM 2019
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""API server for listening to events from github."""

import logging
import os
import sys
from urllib import parse

import flask
import github_webhook

from qiskit_bot import config
from qiskit_bot import repos


LOG = logging.getLogger(__name__)

APP = flask.Flask(__name__)
WEBHOOK = github_webhook.Webhook(APP)

REPOS = {}
CONFIG = None


@APP.before_first_request
def _setup():
    setup()


def get_app():
    return APP


def setup():
    """Setup config."""
    global CONFIG
    if not CONFIG:
        CONFIG = config.load_config('/etc/qiskit_bot.yaml')
    if not os.path.isdir(CONFIG['working_dir']):
        os.mkdir(CONFIG['working_dir'])
    for repo in CONFIG['repos']:
        REPOS[repo] = repos.Repo(CONFIG['working_dir'], repo,
                                 CONFIG['access_token'])


@APP.route("/", methods=['GET'])
def list_routes():
    """List routes on gets to root."""
    output = []
    for rule in APP.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        url = flask.url_for(rule.endpoint, **options)
        out_dict = {
            'name': rule.endpoint,
            'methods': sorted(rule.methods),
            'url': parse.unquote(url),
        }
        output.append(out_dict)
    return flask.jsonify({'routes': output})


@WEBHOOK.hook(event_type='push')
def on_push(data):
    """Handle github pushes."""
    LOG.debug('Received push event for repo: %s sha1: %s' % (
        data['repository']['full_name'], data['after']))
    global REPOS
    print(type(data))
    import pprint
    pprint.pprint(data)
#    data = json.loads(body)
#    repo_name = data['repository']['full_name']
#    git_url = data['repository']['git_url']


def _handle_tag(tag_name, repo):
    pass


@WEBHOOK.hook(event_type='create')
def on_create(data):
    global REPOS
    if data['ref_type']:
        tag_name = data['ref']
        repo_name = data['repository']['full_name']
        _handle_tag(tag_name, REPOS[repo_name])


@WEBHOOK.hook(event_type='pull_request')
def on_pull_event(data):
    pass


@WEBHOOK.hook(event_type='pull_request_review')
def on_pull_request_review(data):
    pass


def main():
    """Run APP."""
    global CONFIG
    CONFIG = config.load_config(sys.argv[1])
    APP.run(debug=True, host='127.0.0.1', port=80)


if __name__ == "__main__":
    main()
