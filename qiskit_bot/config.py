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

import voluptuous as vol
import yaml

LOG = logging.getLogger(__name__)

schema = vol.Schema({
    'api_key': str,
    'working_dir': str,
    'meta_repo': vol.Optional(str),
    'repos': [{
        'name': str,
        'reno': vol.Optional(bool, default=False),
        'branch_on_release': vol.Optional(bool, default=False),
    }],
})


def load_config(path):
    with open(path, 'r') as fd:
        raw_config = yaml.safe_load(fd.read())
    schema(raw_config)
    LOG.info('Loaded config\nRepos: %s' % ','.join(raw_config['repos']))
    if 'meta_repo' in repos:
        LOG.info('meta_repo: %s' % raw_config['meta_repo'])
    return raw_config
