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

import unittest

import fixtures

from qiskit_bot import community


class TestCommunity(fixtures.TestWithFixtures, unittest.TestCase):

    def setUp(self):
        self.temp_dir = fixtures.TempDir()
        self.useFixture(self.temp_dir)

    @unittest.mock.patch("multiprocessing.Process")
    def test_basic_community_pr(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        repo.repo_config = {'uses_community_label': True}
        gh_mock.get_pull.return_value = pr_mock
        data = {
            'number': 1234,
            'user': {'type': 'User'},
            'labels': [
                {'name': 'test_label_1'},
                {'name': 'test_label_2'}
            ]}

        community.add_community_label(data, repo)
        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.add_to_labels.assert_called_once()

    @unittest.mock.patch("multiprocessing.Process")
    def test_repo_not_monitored(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-nature'
        repo.gh_repo = gh_mock
        repo.repo_config = {'uses_community_label': False}
        gh_mock.get_pull.return_value = pr_mock
        data = {
            'number': 1234,
            'user': {'type': 'User'},
            'labels': [
                {'name': 'test_label_1'},
                {'name': 'test_label_2'}
            ]}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_not_called()
        pr_mock.add_to_labels.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_contributor_is_member(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        repo.repo_config = {'uses_community_label': True}
        pr_mock.raw_data = {"author_association": "MEMBER"}
        gh_mock.get_pull.return_value = pr_mock
        data = {
            'number': 1234,
            'user': {'type': 'User'},
            'labels': [
                {'name': 'test_label_1'},
                {'name': 'test_label_2'}
            ]}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_called_once()
        pr_mock.add_to_labels.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_already_labelled(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        repo.repo_config = {'uses_community_label': True}
        gh_mock.get_pull.return_value = pr_mock
        data = {
            'number': 1234,
            'user': {'type': 'User'},
            'labels': [
                {'name': 'Community PR'},
                {'name': 'test_label_2'}
            ]}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_not_called()
        pr_mock.add_to_labels.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_user_is_bot(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        repo.repo_config = {'uses_community_label': True}
        gh_mock.get_pull.return_value = pr_mock
        data = {
            'number': 1234,
            'user': {'type': 'Bot'},
            'labels': [
                {'name': 'Community PR'},
                {'name': 'test_label_2'}
            ]}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_not_called()
        pr_mock.add_to_labels.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_user_is_private_member(self, sub_mock):
        """The data fed to the bot by the webhook is unprivileged, and may
        consider the user to be a contributor if their membership of the
        organisation is private.  The privileged response from `get_pull`
        should contain the correct information, though."""
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        repo.repo_config = {'uses_community_label': True}
        pr_mock.raw_data = {"author_association": "MEMBER"}
        gh_mock.get_pull.return_value = pr_mock
        data = {
            'author_association': "CONTRIBUTOR",
            'number': 1234,
            'user': {'type': 'User'},
            'labels': [
                {'name': 'test_label_1'},
                {'name': 'test_label_2'}
            ]}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_called_once()
        pr_mock.add_to_labels.assert_not_called()
