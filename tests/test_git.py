
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
