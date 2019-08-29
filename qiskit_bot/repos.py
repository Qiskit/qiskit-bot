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
import subprocess

from github import Github

LOG = logging.getLogger(__name__)


class Repo(object):

    def __init__(self, working_dir, repo_name, access_token):
        self.local_path = os.path.join(working_dir, repo_name)
        self.repo_name = repo_name
        self.gh_repo = self._get_gh_repo(access_token)
        self._create_repo()
        self._create_ssh_remote()

    def _create_repo(self):
        LOG.info('Creating local clone of %s at %s' % (self.repo_name,
                                                       self.local_path))
        res = subprocess.run(['git', 'clone',
                              'https://github.com/%s' % self.repo_name,
                              self.local_path],
                             check=True,
                             capture_output=True)
        LOG.debug('git clone https://github.com/%s '
                  '%s\nstdout:\n%s\nstderr:\n%s' % (self.repo_name,
                                                    self.local_path,
                                                    res.stdout, res.stderr))

    def _create_ssh_remote(self):
        LOG.info('Creating ssh remote for %s' % self.repo_name)
        res = subprocess.run(['git', 'remote', 'add', 'github',
                              'git@github.com:%s' % self.repo_name],
                             cwd=self.local_path, capture_output=True,
                             check=True)
        LOG.debug('git remote add github git@github.com/%s\n'
                  'stdout:\n%s\nstderr:\n%s' % (self.repo_name,
                                                res.stdout, res.stderr))

    def _get_gh_repo(self, access_token):
        gh_session = Github(access_token)
        repo = gh_session.get_repo(self.repo_name)
        return repo
