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

import io
import logging
import multiprocessing
import os
import re

import fasteners

from qiskit_bot import git

LOG = logging.getLogger(__name__)

with io.StringIO() as buf:
    buf.write("Thank you for opening a new pull request.\n\n")
    buf.write(
        "Before your PR can be merged it will first need to pass "
        "continuous integration tests and be reviewed. Sometimes "
        "the review process can be slow, so please be patient.\n\n"
    )
    buf.write(
        "While you're waiting, please feel free to review other "
        "open PRs. While only a subset of people are authorized "
        "to approve pull requests for merging, everyone is "
        "encouraged to review open pull requests. Doing reviews "
        "helps reduce the burden on the core team and helps make "
        "the project's code better for everyone.\n"
    )
    DEFAULT_PRELUDE = buf.getvalue()


def trigger_notifications(pr_number, repo, conf):
    """Process any potential notifications on a new PR."""
    working_dir = conf.get('working_dir')
    lock_dir = os.path.join(working_dir, 'lock')

    with fasteners.InterProcessLock(os.path.join(lock_dir, repo.name)):
        git.checkout_default_branch(repo, pull=True)
        local_config = repo.get_local_config()
    notifications_config = local_config.get('notifications')
    always_notify = local_config.get('always_notify')

    def _process_notification():
        notify_list = set()
        if notifications_config:
            notification_regex = {
                re.compile(k): v for k, v in notifications_config.items()
            }
        else:
            notification_regex = {}
        pr = repo.gh_repo.get_pull(pr_number)
        file_list = pr.get_files()
        filenames = [file.filename for file in file_list]
        for path_regex, user_list in notification_regex.items():
            for file_name in filenames:
                if path_regex.search(file_name):
                    for user in user_list:
                        notify_list.add(user)
        if notify_list or always_notify:
            prelude = local_config.get("notification_prelude", DEFAULT_PRELUDE)
            with io.StringIO() as buf:
                # Team members don't get the prelude to make the message
                # less chatty.
                if pr.raw_data["author_association"] not in (
                    "MEMBER", "OWNER"
                ):
                    buf.write(prelude)
                if notify_list:
                    buf.write(
                        "\nOne or more of the following people are "
                        "relevant to this code:\n"
                    )
                    for user in sorted(notify_list):
                        buf.write("- %s\n" % user)
                body = buf.getvalue()
            pr.create_issue_comment(body)

    if notifications_config or always_notify:
        multiprocessing.Process(target=_process_notification).start()
