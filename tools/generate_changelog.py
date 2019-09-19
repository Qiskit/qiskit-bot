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

import os
import sys
import tempfile

from qiskit_bot import config
from qiskit_bot import repos
from qiskit_bot import release_process

if len(sys.argv) != 3:
    print('Usage:\n\tgenerate_changelog.py "ORG/REPONAME" "TAG"')
    print('Example:\n\tgenerate_changelog.py Qiskit/qiskit-terra 0.9.0')
    sys.exit(1)

repo_name = sys.argv[1]
from_tag = sys.argv[2]

with tempfile.TemporaryDirectory() as tmpdir:
    repo = repos.Repo(tmpdir, repo_name, None)
    categories = repo.get_local_config().get(
        'categories', config.default_changelog_categories)

    print(release_process._generate_changelog(
        repo, '%s..' % from_tag, categories))
