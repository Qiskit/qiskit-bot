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

"""Handle git operations."""

import logging
import subprocess

LOG = logging.getLogger(__name__)


def create_branch(branch_name, sha1, repo):
    """Create a branch and push it to github."""

    LOG.info('Creating branch %s for %s' % (branch_name, repo.local_path))
    try:
        res = subprocess.run(['git', 'branch', branch_name, sha1],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Branch create %s for %s, stdout:\n%s\nstderr:\n%s' % (
            branch_name, repo.local_path, res.stdout, res.stderr))
    except subprocess.CalledProcessError:
        LOG.exception('Failed to create a local branch')
        return False
    try:
        LOG.info('Pushing branch %s for %s to github' % (branch_name,
                                                         repo.local_path))
        res = subprocess.run(['git', 'push', branch_name, repo.ssh_remote],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Branch push %s for %s, stdout:\n%s\nstderr:\n%s' % (
            branch_name, repo.local_path, res.stdout, res.stderr))
    except subprocess.CalledProcessError:
        LOG.exception('Failed to push branch to github')
        return False
    return True


def get_git_log(repo, sha1):
    LOG.info('Querying git log of %s for %s' % (sha1, repo.local_path))
    try:
        res = subprocess.run(['git', 'log', '--oneline', sha1],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        return res.stdout
    except subprocess.CalledProcessError:
        LOG.exception('Failed to get git log')
        return ''
