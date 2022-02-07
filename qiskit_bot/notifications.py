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

import fasteners

from qiskit_bot import git

LOG = logging.getLogger(__name__)


def trigger_notifications(pr_number, repo, conf):
    """Do the post tag release processes."""
    working_dir = conf.get('working_dir')
    lock_dir = os.path.join(working_dir, 'lock')

    with fasteners.InterProcessLock(os.path.join(lock_dir, repo.name)):
        git.checkout_default_branch(repo, pull=True)
        local_config = repo.get_local_config()

    def _process_notification():
        notify_list = set()
        notification_regex = {
            re.compile(k): v for k, v in local_config['notifications'].items()
        }
        pr = repo.gh_repo.get_pull(pr_number)
        file_list = pr.get_files()
        filenames = [file.filename for file in file_list]
        for path_regex, user_list in notification_regex.items():
            for file_name in filenames:
                if path_regex.search(file_name):
                    for user in user_list:
                        notify_list.add(user)
        if notify_list:
            default_prelude = """Thank you for opening a new pull request.

Before your PR can be merged it will first need to run and pass continuous
integration tests and be also be reviewed. Sometimes the review process can
be slow, so please be patient.

While you're waiting on CI and for review please feel free to review other open
PRs. While only a subset of people are authorized to approval pull requests for
merging everyone is encouraged to review open pull requests. Doing reviews
helps reduce the burden on the core team and helps make the project's code
better for everyone.

One or more of the the following people are requested to review this:\n
"""
            prelude = local_config.get("notification_prelude", default_prelude)
            with io.StringIO() as buf:
                buf.write(prelude)
                for user in sorted(notify_list):
                    buf.write("- %s\n" % user)
                body = buf.getvalue()
            pr.create_issue_comment(body)
    if 'notifications' in local_config:
        multiprocessing.Process(target=_process_notification).start()
