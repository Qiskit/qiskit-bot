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

import unittest

import fixtures

from qiskit_bot import notifications


class FakeFile:
    """Fake file for get_files() return."""
    def __init__(self, filename):
        self.filename = filename


class TestNotifications(fixtures.TestWithFixtures, unittest.TestCase):

    def setUp(self):
        self.temp_dir = fixtures.TempDir()
        self.useFixture(self.temp_dir)

    @unittest.mock.patch("multiprocessing.Process")
    def test_basic_notification(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*": ["@user1", "@user2"]
            }
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.txt'),
            FakeFile('file2.py')
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = notifications.DEFAULT_PRELUDE + (
            "\nOne or more of the following people are relevant to "
            "this code:\n- @user1\n- @user2\n"
        )
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_no_prelude_for_team_mbembers(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*": ["'@user1'", "'@user2'"]
            }
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.raw_data = {"author_association": "MEMBER"}
        pr_mock.get_files.return_value = [
            FakeFile('file1.txt'),
            FakeFile('file2.py')
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = (
            "\nOne or more of the following people are relevant to "
            "this code:\n- '@user1'\n- '@user2'\n"
        )
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_multiple_overlapping_file_notifications(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*py": ["@user1", "@user2"],
                ".*txt": ["@user2", "@user3"],
            }
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.txt'),
            FakeFile('file2.py')
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = notifications.DEFAULT_PRELUDE + (
            "\nOne or more of the following people are relevant to "
            "this code:\n- @user1\n- @user2\n- @user3\n"
        )

        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_no_matching_files(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*py": ["@user1", "@user2"],
                ".*txt": ["@user2", "@user3"],
            }
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.js'),
            FakeFile('file2.rs')
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_one_hit_multiple_notification_rules(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*py": ["@user1", "@user2"],
                ".*txt": ["@user2", "@user3"],
            }
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.rs'),
            FakeFile('file2.py'),
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = notifications.DEFAULT_PRELUDE + (
            "\nOne or more of the following people are relevant to "
            "this code:\n- @user1\n- @user2\n"
        )
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_no_match_always_notify(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*py": ["@user1", "@user2"],
                ".*txt": ["@user2", "@user3"],
            },
            'always_notify': True,
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.rs'),
            FakeFile('file2.js'),
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = notifications.DEFAULT_PRELUDE
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_no_match_always_notify_custom_prelude(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*py": ["@user1", "@user2"],
                ".*txt": ["@user2", "@user3"],
            },
            'always_notify': True,
            'notification_prelude': "This is my prelude\n"
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.rs'),
            FakeFile('file2.js'),
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = "This is my prelude\n"
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_always_notify_no_notification(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            'always_notify': True,
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.rs'),
            FakeFile('file2.js'),
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = notifications.DEFAULT_PRELUDE
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)

    @unittest.mock.patch("multiprocessing.Process")
    def test_match_custom_prelude(self, sub_mock):
        repo = unittest.mock.MagicMock()
        local_config = {
            "notifications": {
                ".*py": ["@user1", "@user2"],
                ".*txt": ["@user2", "@user3"],
            },
            'always_notify': True,
            'notification_prelude': "This is my prelude\n"
        }
        pr_mock = unittest.mock.MagicMock()
        pr_mock.get_files.return_value = [
            FakeFile('file1.rs'),
            FakeFile('file2.py'),
        ]
        gh_mock = unittest.mock.MagicMock()
        gh_mock.get_pull.return_value = pr_mock
        repo.name = 'test'
        repo.local_config = local_config
        repo.get_local_config = unittest.mock.MagicMock(
            return_value=local_config
        )
        repo.gh_repo = gh_mock
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch('qiskit_bot.git.checkout_default_branch'):
            notifications.trigger_notifications(1234, repo, conf)
        sub_mock.assert_called_once()
        inner_func = sub_mock.call_args_list[0][1]['target']
        inner_func()
        expected_body = """This is my prelude

One or more of the following people are relevant to this code:
- @user1
- @user2
"""
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.create_issue_comment.assert_called_once_with(expected_body)
