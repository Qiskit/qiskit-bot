# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2022
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

MONITORED_REPOS = ['qiskit-terra']
EXCLUDED_USER_TYPES = ['Bot', 'Organization']


def add_community_label(pr_data, repo):
    """Add community label to PR when author not associated with core team"""
    if repo.name in MONITORED_REPOS:
        # check if PR was authored by soemone outside core repo team
        if (pr_data['pull_request']['author_association'] != 'MEMBER'
            ) and (pr_data['pull_request']['user']['type']
                   not in EXCLUDED_USER_TYPES):
            # fetch label data
            labels = pr_data['pull_request']['labels']
            label_names = [label['name'] for label in labels]
            # tag PR with 'community PR's
            if "Community PR" not in label_names:
                pr = repo.gh_repo.get_pull(pr_data['pull_request']['number'])
                pr.add_to_labels("Community PR")
