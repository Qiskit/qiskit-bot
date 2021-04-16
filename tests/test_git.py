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

import subprocess
import unittest

from qiskit_bot import git


class TestGit(unittest.TestCase):

    @unittest.mock.patch('subprocess.run',
                         side_effect=subprocess.CalledProcessError(2, 'git'))
    def test_create_branch_git_exception(self, subprocess_mock):
        repo = unittest.mock.MagicMock()
        res = git.create_branch('stable/0.9', 'sha1', repo)
        self.assertEqual(False, res)

    @unittest.mock.patch('subprocess.run')
    def test_checkout_default_branch_no_config(self, subproc_mock):
        repo_config = {}
        repo = unittest.mock.MagicMock()
        repo.local_path = '/tmp/fake_clone'
        repo.repo_config = repo_config
        git.checkout_default_branch(repo)
        expected_call = unittest.mock.call(['git', 'checkout', 'master'],
                                           capture_output=True, check=True,
                                           cwd='/tmp/fake_clone')
        self.assertEqual(subproc_mock.mock_calls[0], expected_call)
        expected_pull_call = unittest.mock.call(['git', 'pull'],
                                                capture_output=True,
                                                check=True,
                                                cwd='/tmp/fake_clone')
        self.assertEqual(subproc_mock.mock_calls[-1], expected_pull_call)

    @unittest.mock.patch('subprocess.run')
    def test_checkout_default_branch_config(self, subproc_mock):
        repo_config = {'default_branch': 'main'}
        repo = unittest.mock.MagicMock()
        repo.local_path = '/tmp/fake_clone'
        repo.repo_config = repo_config
        git.checkout_default_branch(repo)
        expected_call = unittest.mock.call(['git', 'checkout', 'main'],
                                           capture_output=True, check=True,
                                           cwd='/tmp/fake_clone')
        self.assertEqual(subproc_mock.mock_calls[0], expected_call)
        expected_pull_call = unittest.mock.call(['git', 'pull'],
                                                capture_output=True,
                                                check=True,
                                                cwd='/tmp/fake_clone')
        self.assertEqual(subproc_mock.mock_calls[-1], expected_pull_call)
