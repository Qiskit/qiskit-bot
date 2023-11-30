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


def push_ref_to_github(repo, ref):
    try:
        LOG.info('Pushing ref %s for %s to github' % (ref,
                                                      repo.local_path))
        res = subprocess.run(['git', 'push', repo.ssh_remote, ref],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Branch ref %s for %s, stdout:\n%s\nstderr:\n%s' % (
            ref, repo.local_path, res.stdout, res.stderr))
    except subprocess.CalledProcessError as e:
        LOG.exception(
            'Failed to push branch to github\nstdout:\n%s\nstderr:\n%s'
            % (e.stdout, e.stderr))
        return False


def pull_remote_ref_to_local(repo, ref):
    cmd = ['git', 'pull', 'origin', ref]
    LOG.info('Pulling remote ref %s to local branch' %
             ref)
    try:
        subprocess.run(cmd, capture_output=True, check=True,
                       cwd=repo.local_path)
    except subprocess.CalledProcessError as e:
        LOG.exception('git pull failed\nstdout:\n%s\nstderr:\n%s'
                      % (e.stdout, e.stderr))

        return False
    return True


def create_branch(branch_name, sha1, repo, push=False):
    """Create a branch and push it to github."""

    LOG.info('Creating branch %s for %s' % (branch_name, repo.local_path))
    try:
        res = subprocess.run(['git', 'branch', branch_name, sha1],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Branch create %s for %s, stdout:\n%s\nstderr:\n%s' % (
            branch_name, repo.local_path, res.stdout, res.stderr))
    except subprocess.CalledProcessError as e:
        LOG.exception(
            'Failed to create a local branch\nstdout:\n%s\nstderr:\n%s'
            % (e.stdout, e.stderr))
        return False
    if not push:
        return True
    return push_ref_to_github(repo, branch_name)


def get_git_log(repo, sha1):
    LOG.info('Querying git log of %s for %s' % (sha1, repo.local_path))
    try:
        res = subprocess.run(['git', 'log', '--oneline', sha1],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        return res.stdout
    except subprocess.CalledProcessError as e:
        LOG.exception('Failed to get git log\nstdout:\n%s\nstderr:\n%s'
                      % (e.stdout, e.stderr))
        return ''


def get_tags(repo):
    """Get a list of tags in creation order separated by newlines."""
    LOG.info('Querying git tags for %s' % repo.local_path)
    try:
        res = subprocess.run(['git', 'tag', '--sort=-creatordate'],
                             capture_output=True, check=True, encoding="UTF8",
                             cwd=repo.local_path)
        return res.stdout
    except subprocess.CalledProcessError as e:
        LOG.exception('Failed to get git log\nstdout:\n%s\nstderr:\n%s'
                      % (e.stdout, e.stderr))
        return ''


def clean_repo(repo):
    cmd = ['git', 'clean', '-fdX']
    try:
        subprocess.run(cmd, capture_output=True, check=True,
                       cwd=repo.local_path)
    except subprocess.CompletedProcess as e:
        LOG.exception('git clean failed\nstdout:\n%s\nstderr:\n%s'
                      % (e.stdout, e.stderr))
        return False
    return True


def checkout_ref(repo, ref):
    cmd = ['git', 'checkout', ref]
    LOG.info('Checking out %s of %s' % (ref, repo.local_path))
    try:
        res = subprocess.run(cmd, capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Git checkout for %s, stdout:\n%s\nstderr:\n%s' % (
            repo.local_path, res.stdout, res.stderr))
    except subprocess.CompletedProcess as e:
        LOG.exception('Git checkout failed\nstdout:\n%s\nstderr:\n%s'
                      % (e.stdout, e.stderr))
        return False


def create_git_commit_for_all(repo, commit_msg):
    cmd = ['git', 'commit', '-a', '-m', commit_msg]
    LOG.info('Creating git commit for all local changes in %s' %
             repo.local_path)
    try:
        subprocess.run(cmd, capture_output=True, check=True,
                       cwd=repo.local_path)
    except subprocess.CalledProcessError as e:
        LOG.exception('git commit failed\nstdout:\n%s\nstderr:\n%s'
                      % (e.stdout, e.stderr))
        return False
    return True


def checkout_default_branch(repo, pull=True):
    default_branch = repo.repo_config.get('default_branch', 'master')
    cmd = ['git', 'checkout', default_branch]
    LOG.info('Checking out branch of %s' % repo.local_path)
    try:
        res = subprocess.run(cmd, capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Git checkout for %s, stdout:\n%s\nstderr:\n%s' % (
            repo.local_path, res.stdout, res.stderr))
    except subprocess.CompletedProcess as e:
        LOG.exception('Git checkout failed\nstdout:\n%s\nstderr:\n%s\n'
                      % (e.stdout, e.stderr))
        return False
    if not pull:
        return True
    cmd = ['git', 'pull']
    LOG.info('Pulling the latest default branch for %s' % repo.local_path)
    try:
        subprocess.run(cmd, capture_output=True, check=True,
                       cwd=repo.local_path)
    except subprocess.CompletedProcess as e:
        LOG.exception('Git pull failed\nstdout:\n%s\nstderr:\n%s\n'
                      % (e.stdout, e.stderr))
        return False


def get_latest_tag(repo):
    cmd = ['git', 'describe', '--abbrev=0']
    LOG.info('Getting latest tag for %s' % repo.local_path)
    try:
        res = subprocess.run(cmd, capture_output=True, check=True,
                             cwd=repo.local_path)
    except subprocess.CompletedProcess as e:
        LOG.exception('Git get latest tag failed\nstdout:\n%s\nstderr:\n%s\n'
                      % (e.stdout, e.stderr))
        raise
    return res.stdout


def delete_local_branch(branch_name, repo):
    """Deleting a local branch."""

    LOG.info('Deleting branch %s for %s' % (branch_name, repo.local_path))
    try:
        res = subprocess.run(['git', 'branch', '-D', branch_name],
                             capture_output=True, check=True,
                             cwd=repo.local_path)
        LOG.debug('Branch delete %s for %s, stdout:\n%s\nstderr:\n%s' % (
            branch_name, repo.local_path, res.stdout, res.stderr))
    except subprocess.CalledProcessError as e:
        LOG.exception(
            'Failed to delete a local branch\nstdout:\n%s\nstderr:\n%s\n'
            % (e.stdout, e.stderr))
        return False
    return True
