#!/usr/bin/env python3
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

import argparse
import tempfile

from github import Github

from qiskit_bot import config
from qiskit_bot import repos
from qiskit_bot import release_process


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_name')
    parser.add_argument('tag')
    parser.add_argument('--token', '-t', help="optional token for auth",
                        default=None)
    parser.add_argument(
        '--username', '-u',
        help="optional username for auth, password required if specified",
        default=None)
    parser.add_argument(
        '--password', '-p',
        help="optional password for auth, username required if specified.",
        default=None)
    parser.add_argument(
        '--default-branch', '-b',
        help="the default branch to use for the repository. Defaults to "
             "'main'",
        default='main')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        token = args.token
        repo = repos.Repo(tmpdir, args.repo_name, token,
                          {'default_branch': args.default_branch})
        if not token and args.username and args.password:
            session = Github(args.username, args.password)
            gh_repo = session.get_repo(args.repo_name)
            repo.gh_repo = gh_repo
        categories = repo.get_local_config().get(
            'categories', config.default_changelog_categories)

        print(release_process._generate_changelog(
            repo, '%s..' % args.tag, categories, show_missing=True))


if __name__ == '__main__':
    main()
