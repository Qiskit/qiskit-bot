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

from github import Github


def finish_release(self, version_number, repo, conf):
    """Do the post tag release processes."""
    gh_session = Github(conf['api_key'])
    repo_config = conf['repos'][repo_name]
    if 'meta_repo' in conf:
        meta_repo = gh_session.get_repo(meta_repo)

        if repo_config['reno']:
            pass
