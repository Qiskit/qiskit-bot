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

import io
import logging
import multiprocessing
import os
import re
import shutil
from functools import partial

import fasteners
from packaging.version import parse
import github

from qiskit_bot import config
from qiskit_bot import git

LOG = logging.getLogger(__name__)


def bump_meta(meta_repo, repo, version_number):
    repo_config = repo.repo_config
    git.checkout_default_branch(meta_repo, pull=True)
    version_number_pieces = version_number.split('.')
    meta_version = git.get_latest_tag(meta_repo).decode('utf8')
    meta_version_pieces = meta_version.split('.')
    if repo_config.get('optional_package'):
        return None
    if int(version_number_pieces[2]) == 0:
        new_meta_version = '%s.%s.%s' % (meta_version_pieces[0],
                                         int(meta_version_pieces[1]) + 1, 0)
    else:
        new_meta_version = '%s.%s.%s' % (meta_version_pieces[0],
                                         meta_version_pieces[1],
                                         int(meta_version_pieces[2]) + 1)
    package_name = repo.repo_name.split('/')[1]
    pulls = meta_repo.gh_repo.get_pulls(state='open')
    setup_py_path = os.path.join(meta_repo.local_path, 'setup.py')
    docs_conf_path = os.path.join(
        os.path.join(meta_repo.local_path, 'docs'), 'conf.py')
    title = 'Bump Meta'
    requirements_str = package_name + '==' + version_number
    LOG.info("Processing meta repo bump for %s" % requirements_str)

    bump_pr = None
    for pull in pulls:
        if pull.title == title:
            bump_pr = pull
            git.checkout_ref(meta_repo, 'bump_meta')
            git.pull_remote_ref_to_local(meta_repo, 'bump_meta')
            break
    else:
        branch_name = meta_repo.repo_config.get('default_branch', 'master')
        git.create_branch('bump_meta', 'origin/%s' % branch_name, meta_repo)
        git.checkout_ref(meta_repo, 'bump_meta')
    # Update setup.py
    buf = io.StringIO()
    with open(setup_py_path, 'r') as fd:
        for line in fd:
            if package_name in line:
                old_version = re.search(package_name + '==(.*)', line)[1]
                out_line = line.replace(package_name + '==' + old_version,
                                        requirements_str)
                if not out_line.endswith('",\n') and out_line.endswith('\n'):
                    buf.write(out_line.replace('\n', '",\n'))
            elif 'version=' in line:
                old_version = re.search('version=(.*)', line)[1]
                old_version = old_version.strip('",')
                old_version_pieces = old_version.split('.')
                new_version_pieces = new_meta_version.split('.')
                if old_version != new_meta_version and \
                        old_version_pieces[1] <= new_version_pieces[1]:
                    LOG.debug('Bumping meta version %s to %s' % (
                              old_version, new_meta_version))
                    out_line = line.replace('version="%s"' % old_version,
                                            'version="%s"' % new_meta_version)
                    buf.write(out_line)
                else:
                    LOG.debug('Not bumping meta version %s it is the same or '
                              'less than %s' % (old_version, new_meta_version))
                    buf.write(line)
            else:
                buf.write(line)

    buf.seek(0)
    with open(setup_py_path, 'w') as fd:
        shutil.copyfileobj(buf, fd)
    # Update docs/conf.py
    buf = io.StringIO()
    with open(docs_conf_path, 'r') as fd:
        for line in fd:
            if line.startswith('release = '):
                old_version = re.search('release = "(.*)"', line)[1]
                old_version = old_version.strip('",')
                old_version_pieces = old_version.split('.')
                new_version_pieces = new_meta_version.split('.')
                if old_version != new_meta_version and \
                        old_version_pieces[1] <= new_version_pieces[1]:
                    out_line = line.replace(old_version, new_meta_version)
                    buf.write(out_line)
                else:
                    buf.write(line)
            else:
                buf.write(line)
    buf.seek(0)
    with open(docs_conf_path, 'w') as fd:
        shutil.copyfileobj(buf, fd)

    body = """Bump the meta repo version to include:

%s

""" % requirements_str

    commit_msg = 'Bump version for %s\n\n%s' % (requirements_str, body)
    git.create_git_commit_for_all(meta_repo, commit_msg.encode('utf8'))
    git.push_ref_to_github(meta_repo, 'bump_meta')
    branch_name = meta_repo.repo_config.get('default_branch', 'master')
    if not bump_pr:
        meta_repo.gh_repo.create_pull(title, base=branch_name,
                                      head='bump_meta', body=body)
    else:
        old_body = bump_pr.body
        new_body = old_body + '\n' + requirements_str
        bump_pr.edit(body=new_body)


def _generate_changelog(repo, log_string, categories, show_missing=False):
    git.checkout_default_branch(repo, pull=True)
    git_log = git.get_git_log(repo, log_string).decode('utf8')
    if not git_log:
        return ''
    git_summaries = []
    pr_regex = re.compile(r'^.*\((.*)\)')
    for line in git_log.splitlines():
        pieces = line.split(' ')
        if 'tag:' in line:
            summary = ' '.join(pieces[3:])
            match = pr_regex.match(summary)
            if match:
                pr = match[1][1:]
            else:
                continue
        else:
            summary = ' '.join(pieces[1:])
            match = pr_regex.match(summary)
            if match:
                if match[1][1:]:
                    pr = match[1][1:]
                else:
                    continue
            else:
                continue
        git_summaries.append((summary, pr))
    changelog_dict = {x: [] for x in categories.keys()}
    missing_list = []
    for summary, pr in git_summaries:
        try:
            pr_number = int(pr)
        except ValueError:
            # Invalid PR number
            continue
        try:
            labels = [x.name for x in repo.gh_repo.get_pull(pr_number).labels]
        # If we have an issue querying github for labels this is likely a
        # malformed commit summary line with an invalid PR number so just
        # skip this commit
        except github.GithubException:
            continue
        label_found = False
        for label in labels:
            if label in changelog_dict:
                if categories[label] is None:
                    label_found = True
                    break
                changelog_dict[label].append(summary)
                label_found = True
        if not label_found:
            if show_missing:
                missing_list.append(summary)
    changelog = "# Changelog\n"
    for label in changelog_dict:
        if not changelog_dict[label]:
            continue
        changelog += '## %s\n' % categories[label]
        for pr in changelog_dict[label]:
            entry = '-   %s\n' % pr
            changelog += entry
        changelog += ('\n')
    if show_missing:
        if missing_list:
            changelog += ('\n')
            changelog += '## Missing changelog entry\n'
            for entry in missing_list:
                changelog += '-   %s\n' % entry
    return changelog


def create_github_release(repo, log_string, version_number, categories,
                          prerelease=False):
    changelog = _generate_changelog(repo, log_string, categories)
    release_name = repo.name + ' ' + version_number
    repo.gh_repo.create_git_release(version_number, release_name, changelog,
                                    prerelease=prerelease)


def _get_log_string(version_obj, version_number, repo):
    # If a second prerelease show log from first
    if version_obj.is_prerelease and version_obj.pre[1] > 1:
        old_version = (
            f"{version_obj.base_version}{version_obj.pre[0]}"
            f"{version_obj.pre[1] - 1}"
        )
    # If a patch release log between 0.A.X..0.A.X-1
    elif version_obj.micro > 0:
        old_version = (
            f"{version_obj.major}.{version_obj.minor}."
            f"{version_obj.micro - 1}"
        )
    # If a major version log between X.0.0..x-1.y.z
    elif version_obj.major >= 1 and version_obj.minor == 0:
        tags = git.get_tags(repo)
        previous_major = version_obj.major - 1
        for tag in tags.splitlines():
            tag_version = parse(tag)
            if tag_version.is_prerelease:
                continue
            if tag_version.major == previous_major:
                old_version = tag
                break
    # If a minor release log between Y.X.0..Y.X-1.0
    else:
        old_version = f"{version_obj.major}.{version_obj.minor - 1}.0"
    return f"{version_number}...{old_version}"


# This helper function must be a top-level function to be pickable for
# `multiprocessing`.
def _finish_release__changelog_process(
    version_number, lock_dir, repo, version_obj, is_prerelease
):
    with fasteners.InterProcessLock(os.path.join(lock_dir, repo.name)):
        git.checkout_default_branch(repo, pull=True)
        log_string = _get_log_string(version_obj, version_number, repo)
        categories = repo.get_local_config().get(
            'categories', config.default_changelog_categories)
        create_github_release(repo, log_string, version_number,
                              categories, is_prerelease)
        git.checkout_default_branch(repo, pull=True)


# This helper function must be a top-level function to be pickable for
# `multiprocessing`.
def _finish_release__meta_process(version_number, lock_dir, repo, meta_repo):
    with fasteners.InterProcessLock(os.path.join(lock_dir,
                                                 meta_repo.name)):
        bump_meta(meta_repo, repo, version_number)
        git.checkout_default_branch(meta_repo, pull=True)


def finish_release(version_number, repo, conf, meta_repo):
    """Do the post tag release processes."""
    working_dir = conf.get('working_dir')
    lock_dir = os.path.join(working_dir, 'lock')
    repo_config = repo.repo_config
    version_obj = parse(version_number)
    is_prerelease = version_obj.is_prerelease
    is_postrelease = version_obj.is_postrelease
    version_number_pieces = version_obj.base_version.split('.')
    branch_number = '.'.join(version_number_pieces[:2])

    with fasteners.InterProcessLock(os.path.join(lock_dir, repo.name)):
        # Pull latest default_branch
        git.checkout_default_branch(repo, pull=True)
        if repo_config.get('branch_on_release'):
            branch_name = 'stable/%s' % branch_number
            repo_branches = [x.name for x in repo.gh_repo.get_branches()]
            if int(version_number_pieces[2]) == 0 and \
                    branch_name not in repo_branches:
                if is_prerelease and version_obj.pre[0] != "rc":
                    pass
                else:
                    git.checkout_default_branch(repo, pull=True)
                    git.create_branch(branch_name, version_number, repo,
                                      push=True)

    if not is_postrelease:
        _changelog_process = partial(
            _finish_release__changelog_process,
            version_number,
            lock_dir,
            repo,
            version_obj,
            is_prerelease,
        )
        multiprocessing.Process(target=_changelog_process).start()

    # Only bump the metapackage for tracked/required packages optional extra
    # versions are not pinned and if not a pre-release
    if not repo.repo_config.get('optional_package') and not is_prerelease:
        _meta_process = partial(
            _finish_release__meta_process,
            version_number,
            lock_dir,
            repo,
            meta_repo,
        )
        multiprocessing.Process(target=_meta_process).start()
