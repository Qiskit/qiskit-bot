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

EXCLUDED_USER_TYPES = ['Bot', 'Organization']


def add_community_label(pr_data, repo):
    """Add community label to PR when author not associated with core team"""
    if any((
        not repo.repo_config.get("uses_community_label", False),
        pr_data["user"]["type"] in EXCLUDED_USER_TYPES,
        "Community PR" in [label["name"] for label in pr_data["labels"]],
    )):
        return
    # We need to use the bot's API key rather than public data to know if the
    # user is a private member of the organisation.  PyGitHub doesn't expose
    # the 'author_association' attribute as part of the typed interface.
    pr = repo.gh_repo.get_pull(pr_data["number"])
    if pr.raw_data["author_association"] not in ("MEMBER", "OWNER"):
        pr.add_to_labels("Community PR")
