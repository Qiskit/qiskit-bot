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
