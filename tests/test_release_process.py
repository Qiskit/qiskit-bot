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
from packaging.version import parse

from qiskit_bot import config
from qiskit_bot import release_process

from . import fake_meta  # noqa


class PicklableMagicMock(unittest.mock.MagicMock):
    def __reduce__(self):
        return (unittest.mock.MagicMock, ())


class TestReleaseProcess(fixtures.TestWithFixtures, unittest.TestCase):

    def setUp(self):
        self.temp_dir = fixtures.TempDir()
        self.useFixture(self.temp_dir)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_no_pulls(self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
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
        with open(os.path.join(self.temp_dir.path, 'docs/conf.py'), 'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.1"')
                    break
            else:
                self.fail('Release not updated in doc config')

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
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
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
        with open(os.path.join(self.temp_dir.path, 'docs/conf.py'), 'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_with_existing_pulls(self,
                                                                    git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.19.2'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_called_once_with(meta_repo, 'bump_meta')
        git_mock.pull_remote_ref_to_local.assert_called_once_with(
            meta_repo, 'bump_meta')
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
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_patch_with_no_pulls(self,
                                                              git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.9.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.9.1

Bump the meta repo version to include:

qiskit-terra==0.9.1

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.9.1",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.2",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.2"')
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.9.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_patch_with_unrelated_pulls(self,
                                                                     git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.1'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[
            pull_mock, pull_mock_two])

        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.9.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.9.1

Bump the meta repo version to include:

qiskit-terra==0.9.1

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.9.1",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.2",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.2"')
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.9.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_pending_patch_release_pr(self,
                                                                   git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_called_once_with(meta_repo, 'bump_meta')
        git_mock.pull_remote_ref_to_local.assert_called_once_with(
            meta_repo, 'bump_meta')
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
                    self.assertEqual(line.strip(), 'version="0.15.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_pending_minor_release_pr(self,
                                                                   git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.16.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_called_once_with(meta_repo, 'bump_meta')
        git_mock.pull_remote_ref_to_local.assert_called_once_with(
            meta_repo, 'bump_meta')
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
                    self.assertEqual(line.strip(), 'version="0.16.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.16.0"')
                    break
            else:
                self.fail('Release not updated in doc config')

        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_minor_no_pulls(self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.17.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.17.0

Bump the meta repo version to include:

qiskit-terra==0.17.0

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.17.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.21.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.21.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.17.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_minor_with_unrelated_pulls(self,
                                                                     git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.17.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.17.0

Bump the meta repo version to include:

qiskit-terra==0.17.0

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.17.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.21.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.21.0"')
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.17.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_minor_with_existing_pulls(self,
                                                                    git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.19.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.17.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_called_once_with(meta_repo, 'bump_meta')
        git_mock.pull_remote_ref_to_local.assert_called_once_with(
            meta_repo, 'bump_meta')
        commit_msg = """Bump version for qiskit-terra==0.17.0

Bump the meta repo version to include:

qiskit-terra==0.17.0

"""
        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.17.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.17.0')

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_patch_with_no_pulls(self,
                                                              git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.1'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.10.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.10.0

Bump the meta repo version to include:

qiskit-terra==0.10.0

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.10.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.16.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.16.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.10.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_patch_with_unrelated_pulls(self,
                                                                     git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[
            pull_mock, pull_mock_two])

        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.10.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/master', meta_repo)
        commit_msg = """Bump version for qiskit-terra==0.10.0

Bump the meta repo version to include:

qiskit-terra==0.10.0

"""

        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.10.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.16.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.16.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.10.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_minor_release_from_pending_patch_release_pr(self,
                                                              git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.1',
                                               terra_version='0.15.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.16.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_called_once_with(meta_repo, 'bump_meta')
        git_mock.pull_remote_ref_to_local.assert_called_once_with(
            meta_repo, 'bump_meta')
        commit_msg = """Bump version for qiskit-terra==0.16.0

Bump the meta repo version to include:

qiskit-terra==0.16.0

"""
        git_mock.create_git_commit_for_all.assert_called_once_with(
            meta_repo, commit_msg.encode('utf8'))
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.21.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.21.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.0')

    def test_get_log_string(self):
        version_obj = parse("0.10.2")
        self.assertEqual(
            "0.10.2...0.10.1",
            release_process._get_log_string(
                version_obj, "0.10.2", unittest.mock.MagicMock()
            ),
        )
        version_obj = parse("0.3.0")
        self.assertEqual(
            "0.3.0...0.2.0",
            release_process._get_log_string(
                version_obj, "0.3.0", unittest.mock.MagicMock()
            ),
        )
        version_obj = parse("0.3.25")
        self.assertEqual(
            "0.3.25...0.3.24",
            release_process._get_log_string(
                version_obj, "0.3.25", unittest.mock.MagicMock()
            ),
        )
        version_obj = parse("0.25.0")
        self.assertEqual(
            "0.25.0...0.24.0",
            release_process._get_log_string(
                version_obj, "0.25.0", unittest.mock.MagicMock()
            ),
        )

    @unittest.mock.patch.object(release_process, 'git')
    def test_get_log_string_major_1_0_0(self, git_mock):
        # Tests for >= 1.x.x
        self.useFixture(
            fake_meta.FakeMetaRepo(self.temp_dir, "1.0.0",
                                   terra_version="1.0.0")
        )
        # Mock tags for 1.0.0-0.45.0
        git_mock.get_tags.return_value = """1.0.0
1.0.0rc1
0.46.0
0.45.3
0.45.2
1.0.0b1
0.45.1
0.45.0
"""
        # Prepare mock repo
        mock_repo = unittest.mock.MagicMock()
        mock_repo.name = "qiskit"
        mock_repo.repo_name = "Qiskit/qiskit"
        mock_repo.repo_config = {"optional_package": False}
        mock_repo.local_path = self.temp_dir.path

        # Test for major release 1.0.0
        version_obj = parse("1.0.0")
        self.assertEqual(
            "1.0.0...0.46.0",
            release_process._get_log_string(version_obj, "1.0.0", mock_repo),
        )

    @unittest.mock.patch.object(release_process, 'git')
    def test_get_log_string_post_1_x_x(self, git_mock):
        # Tests for >= 1.x.x
        self.useFixture(
            fake_meta.FakeMetaRepo(self.temp_dir, "1.1.0",
                                   terra_version="1.1.1")
        )
        # Mock tags for 1.1.1-0.45.0
        git_mock.get_tags.return_value = """0.46.2
1.1.1
0.46.2
1.1.1
1.1.0
1.1.0rc1
0.46.1
1.0.2
1.0.1
1.0.0
1.0.0rc1
0.46.0
0.45.3
0.45.2
1.0.0b1
0.45.1
0.45.0
"""
        mock_repo = unittest.mock.MagicMock()
        mock_repo.name = "qiskit"
        mock_repo.repo_name = "Qiskit/qiskit"
        mock_repo.repo_config = {"optional_package": False}
        mock_repo.local_path = self.temp_dir.path

        # Test minor release 1.1.0
        version_obj = parse("1.1.0")
        self.assertEqual(
            "1.1.0...1.0.0",
            release_process._get_log_string(version_obj, "1.1.0", mock_repo),
        )

        # Test bugfix release 1.1.1
        version_obj = parse("1.1.1")
        self.assertEqual(
            "1.1.1...1.1.0",
            release_process._get_log_string(version_obj, "1.1.1", mock_repo),
        )

    @unittest.mock.patch.object(release_process, 'git')
    def test_get_log_string_post_2_x_x(self, git_mock):
        # Tests for >= 2.x.x
        self.useFixture(
            fake_meta.FakeMetaRepo(self.temp_dir, "1.1.0",
                                   terra_version="1.1.1")
        )
        # Mock tags for 2.0.0rc1-1.3.0rc1
        git_mock.get_tags.return_value = """2.0.0
2.0.0.rc1
1.4.0
1.4.0rc1
1.3.2
1.3.1
1.3.0
1.2.2
1.3.0rc1
"""
        # Prepare mock repository
        mock_repo = unittest.mock.MagicMock()
        mock_repo.name = "qiskit"
        mock_repo.repo_name = "Qiskit/qiskit"
        mock_repo.repo_config = {"optional_package": False}
        mock_repo.local_path = self.temp_dir.path

        # Test for release candidate 1.4.0rc1
        version_obj = parse("1.4.0rc1")
        self.assertEqual(
            "1.4.0rc1...1.3.0",
            release_process._get_log_string(version_obj, "1.4.0rc1",
                                            mock_repo),
        )

        # Test for minor release 1.4.0
        version_obj = parse("1.4.0")
        self.assertEqual(
            "1.4.0...1.3.0",
            release_process._get_log_string(version_obj, "1.4.0", mock_repo),
        )

        # Test for major release candidate 2.0.0rc1
        version_obj = parse("2.0.0rc1")
        self.assertEqual(
            "2.0.0rc1...1.4.0",
            release_process._get_log_string(version_obj, "2.0.0rc1",
                                            mock_repo),
        )

        # Test for major release 2.0.0
        version_obj = parse("2.0.0")
        self.assertEqual(
            "2.0.0...1.4.0",
            release_process._get_log_string(version_obj, "2.0.0",
                                            mock_repo),
        )

    def test_get_log_string_prerelease(self):
        version_obj = parse("0.25.0rc1")
        self.assertEqual('0.25.0rc1...0.24.0',
                         release_process._get_log_string(
                             version_obj,
                             "0.25.0rc1",
                             unittest.mock.MagicMock()))
        version_obj = parse("0.25.0rc2")
        self.assertEqual('0.25.0rc2...0.25.0rc1',
                         release_process._get_log_string(
                             version_obj,
                             "0.25.0rc2",
                             unittest.mock.MagicMock()))
        version_obj = parse("0.25.0b1")
        self.assertEqual('0.25.0b1...0.24.0',
                         release_process._get_log_string(
                             version_obj,
                             "0.25.0b1",
                             unittest.mock.MagicMock()))

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_release(self, bump_meta_mock, github_release_mock,
                            git_mock):
        meta_repo = PicklableMagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = PicklableMagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_config = {'branch_on_release': False}
        conf = {'working_dir': self.temp_dir.path}
        release_process.finish_release('0.12.0', repo, conf, meta_repo)
        bump_meta_mock.called_once_with(meta_repo, repo, '0.12.0')
        github_release_mock.called_once_with(
            repo, '0.12.0...0.11.0', '0.12.0',
            config.default_changelog_categories)
        git_mock.create_branch.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_release_with_branch(self, bump_meta_mock,
                                        github_release_mock,
                                        git_mock):
        meta_repo = PicklableMagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = PicklableMagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo.get_branches.return_value = []
        repo.repo_config = {'branch_on_release': True}
        conf = {'working_dir': self.temp_dir.path}
        release_process.finish_release('0.12.0', repo, conf, meta_repo)
        bump_meta_mock.called_once_with(meta_repo, repo, '0.12.0')
        github_release_mock.called_once_with(
            repo, '0.12.0...0.11.0', '0.12.0',
            config.default_changelog_categories)
        git_mock.create_branch.assert_called_once_with(
            'stable/0.12', '0.12.0', repo, push=True)

    @unittest.mock.patch.object(release_process, 'git')
    def test_generate_changelog_with_invalid_PR_number(self, git_mock):
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo.get_branches.return_value = []
        repo.repo_config = {'branch_on_release': True}
        fake_log = """403bc40f8 Add PauliSumOp (Qiskit/qiskit-aqua#1440)
5a7f41344 Tune performance of optimize_1q_decomposition (#5682)
6e2542243 Change collect_1q_runs return for performance (#5685)
25eb58a29 Add unroll step to level2 passmanager optimization loop (#5671)
"""
        git_mock.get_git_log.return_value = fake_log.encode('utf8')
        res = release_process._generate_changelog(
            repo, '0.17.0...0.16.0',
            config.default_changelog_categories, True)
        expected = """# Changelog

## Missing changelog entry
-   Tune performance of optimize_1q_decomposition (#5682)
-   Change collect_1q_runs return for performance (#5685)
-   Add unroll step to level2 passmanager optimization loop (#5671)
"""
        self.assertEqual(res, expected)

    @unittest.mock.patch.object(release_process, 'git')
    def test_generate_changelog_with_changelog_none(self, git_mock):
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.gh_repo.get_branches.return_value = []
        repo.gh_repo = unittest.mock.MagicMock()

        def fake_get_pull(number):
            result = unittest.mock.MagicMock()
            if number == 5685:
                labels_obj = unittest.mock.MagicMock()
                labels_obj.name = 'Changelog: None'
                result.labels = [labels_obj]
            else:
                result.labels = []
            return result

        repo.gh_repo.get_pull = fake_get_pull
        repo.repo_config = {'branch_on_release': True}
        fake_log = """
5a7f41344 Tune performance of optimize_1q_decomposition (#5682)
6e2542243 Change collect_1q_runs return for performance (#5685)
25eb58a29 Add unroll step to level2 passmanager optimization loop (#5671)
"""
        git_mock.get_git_log.return_value = fake_log.encode('utf8')
        res = release_process._generate_changelog(
            repo, '0.17.0...0.16.0',
            config.default_changelog_categories, True)
        expected = """# Changelog

## Missing changelog entry
-   Tune performance of optimize_1q_decomposition (#5682)
-   Add unroll step to level2 passmanager optimization loop (#5671)
"""
        self.assertEqual(res, expected)

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_no_pulls_optional_package(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs/conf.py'), 'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')

        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_with_unrelated_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs/conf.py'), 'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_with_existing_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.19.2'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        version_number = '0.16.1'
        repo.repo_config = {'optional_package': True}

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_not_called()
        git_mock.pull_remote_ref_to_local.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_patch_with_no_pulls_optional_package(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.9.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.9.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_patch_with_unrelated_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.1'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[
            pull_mock, pull_mock_two])

        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.9.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.9.1",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_pending_patch_release_pr_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_not_called()
        git_mock.pull_remote_ref_to_local.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_pending_minor_release_pr_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.16.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_not_called()
        git_mock.pull_remote_ref_to_local.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.16.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.16.0"')
                    break
            else:
                self.fail('Release not updated in doc config')

        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_minor_no_pulls_optional(self,
                                                                  git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.17.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_minor_with_unrelated_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.17.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')

        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_minor_with_existing_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.19.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.17.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_not_called()
        git_mock.pull_remote_ref_to_local.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.16.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.0",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.0"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_patch_with_no_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.1'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.10.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.9.1",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_minor_release_from_patch_with_unrelated_pulls_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.15.1',
                                               terra_version='0.9.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.15.1'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[
            pull_mock, pull_mock_two])

        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.10.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.9.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.15.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.15.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_minor_release_from_pending_patch_release_pr_optional(
            self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.1',
                                               terra_version='0.15.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        pull_mock = unittest.mock.MagicMock()
        pull_mock.title = 'Fix docs'
        pull_mock_two = unittest.mock.MagicMock()
        pull_mock_two.title = 'More docs fixes and fun'
        existing_pull_mock = unittest.mock.MagicMock()
        existing_pull_mock.title = 'Bump Meta'
        existing_pull_mock.body = 'Fake old body'
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(
            return_value=[pull_mock, pull_mock_two, existing_pull_mock])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': True}
        version_number = '0.16.0'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_not_called()
        git_mock.checkout_ref.assert_not_called()
        git_mock.pull_remote_ref_to_local.assert_not_called()
        git_mock.create_git_commit_for_all.assert_not_called()
        with open(os.path.join(self.temp_dir.path, 'setup.py'), 'r') as fd:
            terra_bump = False
            meta_bump = False
            for line in fd:
                if 'qiskit-terra' in line:
                    self.assertEqual(line.strip(), '"qiskit-terra==0.15.0",')
                    terra_bump = True
                elif 'version=' in line:
                    self.assertEqual(line.strip(), 'version="0.20.1",')
                    meta_bump = True
                else:
                    continue
            self.assertTrue(terra_bump)
            self.assertTrue(meta_bump)
        with open(os.path.join(self.temp_dir.path, 'docs', 'conf.py'),
                  'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.1"')
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    def test_bump_meta_patch_release_from_minor_no_pulls_main(self, git_mock):
        self.useFixture(fake_meta.FakeMetaRepo(self.temp_dir, '0.20.0',
                                               terra_version='0.16.0'))
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {'default_branch': 'main'}
        git_mock.get_latest_tag = unittest.mock.MagicMock(
            return_value='0.20.0'.encode('utf8'))
        meta_repo.gh_repo.get_pulls = unittest.mock.MagicMock(return_value=[])
        meta_repo.local_path = self.temp_dir.path
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_name = 'Qiskit/qiskit-terra'
        repo.repo_config = {'optional_package': False}
        version_number = '0.16.1'

        release_process.bump_meta(meta_repo, repo, version_number)
        git_mock.create_branch.assert_called_once_with(
            'bump_meta', 'origin/main', meta_repo)
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
        with open(os.path.join(self.temp_dir.path, 'docs/conf.py'), 'r') as fd:
            for line in fd:
                if 'release = ' in line:
                    self.assertEqual(line.strip(), 'release = "0.20.1"')
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='main', head='bump_meta', body=body)

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_prerelease(self, bump_meta_mock, github_release_mock,
                               git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_config = {'branch_on_release': True}
        repo.get_local_config = lambda: {}
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch.object(
                release_process, 'multiprocessing'
        ) as mp_mock:
            mp_mock.Process = ProcessMock
            release_process.finish_release('0.12.0rc1', repo, conf, meta_repo)
        git_mock.create_branch.assert_called_once_with(
            "stable/0.12", "0.12.0rc1", repo, push=True
        )
        github_release_mock.assert_called_once_with(
            repo, '0.12.0rc1...0.11.0', '0.12.0rc1',
            config.default_changelog_categories, True)
        bump_meta_mock.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_release_with_pre_existing_branch(self, bump_meta_mock,
                                                     github_release_mock,
                                                     git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        # After a pre-release we've already created a stable branch so we
        # should create a bump meta pr and not create a branch.
        fake_branch = unittest.mock.MagicMock()
        fake_branch.name = "stable/0.12"
        repo.gh_repo.get_branches.return_value = [fake_branch]
        repo.repo_config = {'branch_on_release': True}
        repo.get_local_config = lambda: {}
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch.object(
                release_process, 'multiprocessing'
        ) as mp_mock:
            mp_mock.Process = ProcessMock
            release_process.finish_release('0.12.0', repo, conf, meta_repo)
        git_mock.create_branch.assert_not_called()
        bump_meta_mock.called_once_with(meta_repo, repo, '0.12.0')
        github_release_mock.assert_called_once_with(
            repo, '0.12.0...0.11.0', '0.12.0',
            config.default_changelog_categories, False)

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_prerelease_with_pre_existing_branch(self, bump_meta_mock,
                                                        github_release_mock,
                                                        git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        # After a pre-release we've already created a stable branch so we
        # should create a bump meta pr and not create a branch.
        fake_branch = unittest.mock.MagicMock()
        fake_branch.name = "stable/0.12"
        repo.gh_repo.get_branches.return_value = [fake_branch]
        repo.repo_config = {'branch_on_release': True}
        repo.get_local_config = lambda: {}
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch.object(
                release_process, 'multiprocessing'
        ) as mp_mock:
            mp_mock.Process = ProcessMock
            release_process.finish_release('0.12.0rc2', repo, conf, meta_repo)
        bump_meta_mock.assert_not_called()
        github_release_mock.assert_called_once_with(
            repo, '0.12.0rc2...0.12.0rc1', '0.12.0rc2',
            config.default_changelog_categories, True)
        git_mock.create_branch.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_prerelease_non_rc(self, bump_meta_mock,
                                      github_release_mock, git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_config = {'branch_on_release': True}
        repo.get_local_config = lambda: {}
        conf = {'working_dir': self.temp_dir.path}
        with unittest.mock.patch.object(
                release_process, 'multiprocessing'
        ) as mp_mock:
            mp_mock.Process = ProcessMock
            release_process.finish_release('0.12.0b1', repo, conf, meta_repo)
        git_mock.create_branch.assert_not_called()
        github_release_mock.assert_called_once_with(
            repo, '0.12.0b1...0.11.0', '0.12.0b1',
            config.default_changelog_categories, True)
        bump_meta_mock.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_major_version_prerelease_non_rc(self, bump_meta_mock,
                                                    github_release_mock,
                                                    git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_config = {'branch_on_release': True}
        repo.get_local_config = lambda: {}
        conf = {'working_dir': self.temp_dir.path}

        def tag_history(*args, **kwargs):
            return """1.0.0b1
0.45.1
0.45.0
0.25.3
0.45.0rc1
0.25.2.1
0.25.2
0.25.1
0.25.0
0.25.0rc1
0.24.2
0.24.1
"""
        git_mock.get_tags = tag_history
        with unittest.mock.patch.object(
                release_process, 'multiprocessing'
        ) as mp_mock:
            mp_mock.Process = ProcessMock
            release_process.finish_release('1.0.0b1', repo, conf, meta_repo)
        git_mock.create_branch.assert_not_called()
        github_release_mock.assert_called_once_with(
            repo, '1.0.0b1...0.45.1', '1.0.0b1',
            config.default_changelog_categories, True)
        bump_meta_mock.assert_not_called()

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_major_version_prerelease_rc(self, bump_meta_mock,
                                                github_release_mock,
                                                git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
        repo.name = 'qiskit-terra'
        repo.repo_config = {'branch_on_release': True}
        repo.get_local_config = lambda: {}
        conf = {'working_dir': self.temp_dir.path}

        def tag_history(*args, **kwargs):
            return """1.0.0rc1
1.0.0b1
0.45.1
0.45.0
0.25.3
0.45.0rc1
0.25.2.1
0.25.2
0.25.1
0.25.0
0.25.0rc1
0.24.2
0.24.1
"""

        git_mock.get_tags = tag_history
        with unittest.mock.patch.object(
                release_process, 'multiprocessing'
        ) as mp_mock:
            mp_mock.Process = ProcessMock
            release_process.finish_release('1.0.0rc1', repo, conf, meta_repo)
        git_mock.create_branch.assert_called_once_with(
            "stable/1.0", "1.0.0rc1", repo, push=True
        )
        github_release_mock.assert_called_once_with(
            repo, '1.0.0rc1...0.45.1', '1.0.0rc1',
            config.default_changelog_categories, True)
        bump_meta_mock.assert_not_called()


class ProcessMock:

    def __init__(self, target=None):
        self.target = target

    def start(self):
        self.target()
