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


def add_community_label(pr_data, repo):
    """Add community label to PR when author not associated with core team"""
    if repo.name in MONITORED_REPOS:
        # check if PR was authored by soemone outside core repo team
        if pr_data['pull_request']['author_association'] != 'MEMBER':
            # fetch PR metadata
            pr = repo.gh_repo.get_pull(pr_data['pull_request']['number'])
            # tag PR with 'community PR' label & notify reviewers
            labels = pr.get_labels()
            label_names = [label['name'] for label in labels]
            if "Community PR" not in label_names:
                pr.add_to_labels("Community PR")
                pr.create_review_request(
                    team_reviewers=["community-reviewers"])
