# -*- coding: utf-8 -*-

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

import logging
import os

import voluptuous as vol
import yaml


LOG = logging.getLogger(__name__)


default_changelog_categories = {
    'Changelog: Deprecation': 'Deprecated',
    'Changelog: New Feature': 'Added',
    'Changelog: API Change': 'Changed',
    'Changelog: Removal': 'Removed',
    'Changelog: Bugfix': 'Fixed',
}


schema = vol.Schema({
    'api_key': str,
    'working_dir': str,
    'meta_repo': vol.Optional(str, default='Qiskit/qiskit'),
    'github_webhook_secret': vol.Optional(str),
    'repos': [{
        'name': str,
        'branch_on_release': vol.Optional(bool, default=False),
    }],
})


def load_config(path):
    with open(path, 'r') as fd:
        raw_config = yaml.safe_load(fd.read())
    schema(raw_config)
    LOG.info('Loaded config\nRepos: %s' % ','.join(
        [x['name'] for x in raw_config['repos']]))
    if 'meta_repo' in raw_config:
        LOG.info('meta_repo: %s' % raw_config['meta_repo'])
    return raw_config


local_config_schema = vol.Schema({
    'users': [{}],
    'categories': vol.Optional({}),
})


def load_repo_config(repo):
    config_path = os.path.join(repo.local_path, 'qiskit_bot.yaml')
    if not os.path.isfile(config_path):
        return {'users': [], 'categories': default_changelog_categories}
    with open(config_path, 'r') as fd:
        raw_config = yaml.safe_load(fd.read())
    try:
        local_config_schema(raw_config)
    except vol.MultipleInvalid:
        LOG.exception('Invalid local repo config for %s' % repo.repo_name)
        return None
    LOG.info('Loaded local repo config for %s' % repo.repo_name)
    return raw_config
