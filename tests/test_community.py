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
        gh_mock.get_pull.return_value = pr_mock
        pr_mock.get_labels.return_value = [{
            'name': 'test_label_1'}, {'name': 'test_label_2'}]
        data = {'pull_request': {'author_association': None, 'number': 1234}}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.get_labels.assert_called_once()
        pr_mock.add_to_labels.assert_called_once()
        pr_mock.create_review_request.assert_called_once()

    @unittest.mock.patch("multiprocessing.Process")
    def test_repo_not_monitored(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-nature'
        repo.gh_repo = gh_mock
        gh_mock.get_pull.return_value = pr_mock
        pr_mock.get_labels.return_value = [{
            'name': 'test_label_1'}, {'name': 'test_label_2'}]
        data = {'pull_request': {'author_association': None, 'number': 1234}}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_not_called()
        pr_mock.get_labels.assert_not_called()
        pr_mock.add_to_labels.assert_not_called()
        pr_mock.create_review_request.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_contributor_is_member(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        gh_mock.get_pull.return_value = pr_mock
        pr_mock.get_labels.return_value = [{
            'name': 'test_label_1'}, {'name': 'test_label_2'}]
        data = {
            'pull_request': {'author_association': 'MEMBER', 'number': 1234}}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_not_called()
        pr_mock.get_labels.assert_not_called()
        pr_mock.add_to_labels.assert_not_called()
        pr_mock.create_review_request.assert_not_called()

    @unittest.mock.patch("multiprocessing.Process")
    def test_already_labelled(self, sub_mock):
        repo = unittest.mock.MagicMock()
        pr_mock = unittest.mock.MagicMock()
        gh_mock = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo = gh_mock
        gh_mock.get_pull.return_value = pr_mock
        pr_mock.get_labels.return_value = [{
            'name': 'Community PR'}, {'name': 'test_label_2'}]
        data = {'pull_request': {'author_association': None, 'number': 1234}}

        community.add_community_label(data, repo)

        gh_mock.get_pull.assert_called_once_with(1234)
        pr_mock.get_labels.assert_called_once()
        pr_mock.add_to_labels.assert_not_called()
        pr_mock.create_review_request.assert_not_called()
