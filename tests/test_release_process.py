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

from qiskit_bot import config
from qiskit_bot import release_process

from . import fake_meta  # noqa


class TestReleaseProcess(fixtures.TestWithFixtures, unittest.TestCase):

    def setUp(self):
        self.temp_dir = fixtures.TempDir()
        self.useFixture(self.temp_dir)
        self.generate = unittest.mock.patch.object(
            release_process, '_regenerate_authors')
        self.generate_mock = self.generate.start()

    def tearDown(self):
        self.generate.stop()

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.2'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.9.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.2'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.9.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.1'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.16.0'")
                    break
            else:
                self.fail('Release not updated in doc config')

        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.21.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.17.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.21.0'")
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.17.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.17.0')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.16.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.10.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.16.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.10.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.21.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.0')
        self.generate_mock.called_once_with(meta_repo)

    def test_get_log_string(self):
        version_pieces = ['0', '10', '2']
        self.assertEqual('0.10.2...0.10.1',
                         release_process._get_log_string(version_pieces))
        version_pieces = ['0', '3', '0']
        self.assertEqual('0.3.0...0.2.0',
                         release_process._get_log_string(version_pieces))
        version_pieces = ['0', '3', '25']
        self.assertEqual('0.3.25...0.3.24',
                         release_process._get_log_string(version_pieces))
        version_pieces = ['0', '25', '0']
        self.assertEqual('0.25.0...0.24.0',
                         release_process._get_log_string(version_pieces))

    @unittest.mock.patch.object(release_process, 'git')
    @unittest.mock.patch.object(release_process, 'create_github_release')
    @unittest.mock.patch.object(release_process, 'bump_meta')
    def test_finish_release(self, bump_meta_mock, github_release_mock,
                            git_mock):
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
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
        meta_repo = unittest.mock.MagicMock()
        meta_repo.repo_config = {}
        meta_repo.name = 'qiskit'
        repo = unittest.mock.MagicMock()
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
        fake_log = """5a7f41344 Tune performance of optimize_1q_decomposition (#5682)
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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.2'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.9.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.2'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.9.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.1'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.16.0'")
                    break
            else:
                self.fail('Release not updated in doc config')

        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.1')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.17.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.17.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.0'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.17.0')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.2'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.10.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.15.2'")
                    break
            else:
                self.fail('Release not updated in doc config')
        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.10.0\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='master', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')
        meta_repo.gh_repo.create_pull.assert_not_called()
        existing_pull_mock.edit.assert_called_once_with(
            body='Fake old body\nqiskit-terra==0.16.0')
        self.generate_mock.called_once_with(meta_repo)

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
                    self.assertEqual(line.strip(), "release = '0.20.1'")
                    break
            else:
                self.fail('Release not updated in doc config')

        body = ("Bump the meta repo version to include:\n\n"
                "qiskit-terra==0.16.1\n\n")
        meta_repo.gh_repo.create_pull.assert_called_once_with(
            'Bump Meta', base='main', head='bump_meta', body=body)
        self.generate_mock.called_once_with(meta_repo)
