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

import fasteners
import flask
import github_webhook

from qiskit_bot import config
from qiskit_bot import git
from qiskit_bot import community
from qiskit_bot import notifications
from qiskit_bot import release_process
from qiskit_bot import repos


LOG = logging.getLogger(__name__)

APP = flask.Flask(__name__)
WEBHOOK = github_webhook.Webhook(APP)

REPOS = {}
META_REPO = None
CONFIG = None


@APP.before_first_request
def _setup():
    setup()


def get_app():
    return APP


def setup():
    """Setup config."""
    global CONFIG
    global META_REPO
    global WEBHOOK
    if not CONFIG:
        CONFIG = config.load_config('/etc/qiskit_bot.yaml')
    log_level = CONFIG.get('log_level', 'INFO')
    default_log_format = ('%(asctime)s: %(process)d %(levelname)s '
                          '%(name)s [-] %(message)s')
    log_format = CONFIG.get('log_format', default_log_format)

    logging.basicConfig(level=log_level, format=log_format)
    if not os.path.isdir(CONFIG['working_dir']):
        os.mkdir(CONFIG['working_dir'])
    if not os.path.isdir(os.path.join(CONFIG['working_dir'], 'lock')):
        os.mkdir(os.path.join(CONFIG['working_dir'], 'lock'))
    for repo in CONFIG['repos']:

        with fasteners.InterProcessLock(
                os.path.join(os.path.join(CONFIG['working_dir'], 'lock'),
                             repo['name'])):
            REPOS[repo['name']] = repos.Repo(CONFIG['working_dir'],
                                             repo['name'],
                                             CONFIG['api_key'],
                                             repo_config=repo)
    # Load the meta repo
    with fasteners.InterProcessLock(
            os.path.join(os.path.join(CONFIG['working_dir'], 'lock'),
                         CONFIG['meta_repo'])):
        repo_config = {'default_branch': CONFIG['meta_repo_default_branch']}
        META_REPO = repos.Repo(CONFIG['working_dir'], CONFIG['meta_repo'],
                               CONFIG['api_key'], repo_config=repo_config)
    # NOTE(mtreinish): This is a workaround until there is a supported method
    # to set a secret post-init. See:
    # https://github.com/bloomberg/python-github-webhook/pull/19
    if CONFIG.get('github_webhook_secret', None):
        secret = CONFIG['github_webhook_secret']
        if not isinstance(secret, bytes):
            secret = secret.encode("utf-8")
        WEBHOOK._secret = secret


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


@WEBHOOK.hook(event_type='create')
def on_create(data):
    global REPOS
    if data['ref_type'] == 'tag':
        tag_name = data['ref']
        repo_name = data['repository']['full_name']
        if repo_name in REPOS:
            release_process.finish_release(tag_name, REPOS[repo_name],
                                           CONFIG, META_REPO)
        else:
            LOG.warn('Recieved webhook event for %s, but this is not a '
                     'configured repository.' % repo_name)


@WEBHOOK.hook(event_type='pull_request')
def on_pull_event(data):
    global META_REPO
    global CONFIG
    if data['action'] == 'closed':
        if data['repository']['full_name'] == META_REPO.repo_name:
            if data['pull_request']['title'] == 'Bump Meta':
                with fasteners.InterProcessLock(
                    os.path.join(os.path.join(CONFIG['working_dir'], 'lock'),
                                 META_REPO.name)):
                    # Delete github branch:
                    META_REPO.gh_repo.get_git_ref(
                        "heads/" 'bump_meta').delete()
                    # Delete local branch
                    git.checkout_default_branch(META_REPO)
                    git.delete_local_branch('bump_meta', META_REPO)

    if data['action'] in ('opened', 'ready_for_review'):
        repo_name = data['repository']['full_name']
        pr_number = data['pull_request']['number']
        if repo_name in REPOS:
            community.add_community_label(
                data["pull_request"], REPOS[repo_name]
            )
            if not data['pull_request']['draft']:
                notifications.trigger_notifications(
                    pr_number, REPOS[repo_name], CONFIG
                )


@WEBHOOK.hook(event_type='pull_request_review')
def on_pull_request_review(data):
    pass


def main():
    """Run APP."""
    global CONFIG
    CONFIG = config.load_config(sys.argv[1])
    log_format = ('%(asctime)s %(process)d %(levelname)s '
                  '%(name)s [-] %(message)s')
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    APP.run(debug=True, host='0.0.0.0', port=8281)


if __name__ == "__main__":
    main()
