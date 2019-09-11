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

import fnmatch

from qiskit_bot import git


def _check_reviewers(pr, reviewers):
    approvers_list = []
    files = [x.filename for x in pr.get_files()]
    for f in files:
        for pattern in reviewers:
            if fnmatch.fnmatch(f, pattern):
                approvers_list += reviewers[pattern]
    owner = pr.user.login
    # Get most recent reviews
    reviews = {}
    for review in pr.get_reviews():
        if review.user.login == owner:
            continue
        if review.user.login not in reviews:
            reviewers[review.user.login] = review
        elif reviewers[review.user.login].submitted_at < review.submitted_at:
            reviewers[review.user.login] = review
    # Check if required approvers have approved or rejected
    for review


    

def check_preconditions(pr, repo):
    with fasteners.InterProcessLock(
            os.path.join(os.path.join(CONFIG['working_dir'], 'lock'),
                         repo.name)):
        git.checkout_master(repo, pull=True)
        local_config = repo.get_local_config()
        pull_request = repo.gh_repo.get_pull(int(pr))
        if not local_config.get('users'):
            return False

        reviewers = local_config['users'].get('reviewers', {})
        reviewed = _check_reviewers(pull_request, reviewers)
        if reviewed and pull_request.mergeable:



def merge_pr(pr):
    pass


def rebase_pr(pr):
    pass
