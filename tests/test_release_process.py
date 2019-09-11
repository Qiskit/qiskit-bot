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

import os
import unittest

import fixtures

from qiskit_bot import release_process

from . import fake_meta  # noqa


class TestReleaseProcess(fixtures.TestWithFixtures, unittest.TestCase):

    def setUp(self):
        self.temp_dir = fixtures.TempDir()
        self.useFixture(self.temp_dir)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_no_pulls(self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        meta_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.16.1

Bump the meta repo version to include:

qiskit-terra==0.16.1

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.1",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_with_unrelated_pulls(self,
                                                                     git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        meta_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.16.1

Bump the meta repo version to include:

qiskit-terra==0.16.1

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.1",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
