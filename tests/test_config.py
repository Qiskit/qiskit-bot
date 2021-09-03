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

import voluptuous as vol

from qiskit_bot import config


class TestConfig(unittest.TestCase):

    def test_load_config_empty(self):
        mock_open = unittest.mock.mock_open(read_data='')
        with unittest.mock.patch('qiskit_bot.config.open', mock_open):
            self.assertRaises(vol.MultipleInvalid, config.load_config,
                              'fake_path')

    def test_load_config_invalid_path(self):
        self.assertRaises(FileNotFoundError, config.load_config,
                          'this_is_completely_invalid_path.yaml')

    def test_load_config_missing_working_dir(self):
        config_text = """
        api_key: 1234567abc
        github_webhook_secret: 12345abc
        meta_repo: foo
        """
        mock_open = unittest.mock.mock_open(read_data=config_text)
        with unittest.mock.patch('qiskit_bot.config.open', mock_open):
            self.assertRaises(vol.MultipleInvalid, config.load_config,
                              'fake_path')

    def test_load_config_minimal(self):
        config_text = """
        api_key: 1234567abc
        working_dir: /tmp
        meta_repo: Qiskit/qiskit
        repos:
          - name: qiskit/Qiskit-terra
        """
        mock_open = unittest.mock.mock_open(read_data=config_text)
        with unittest.mock.patch('qiskit_bot.config.open', mock_open):
            res = config.load_config('fake_path')
        self.assertEqual('/tmp', res['working_dir'])
        self.assertEqual('1234567abc', res['api_key'])
        # Meta repo defaults to Qiskit/qiskit
        self.assertEqual('Qiskit/qiskit', res['meta_repo'])

    def test_load_config_empty_repos(self):
        config_text = """
        api_key: 1234567abc
        github_webhook_secret: 12345abc
        meta_repo: mtreinish/qiskit-sandbox
        repos:
        """
        mock_open = unittest.mock.mock_open(read_data=config_text)
        with unittest.mock.patch('qiskit_bot.config.open', mock_open):
            self.assertRaises(vol.MultipleInvalid, config.load_config,
                              'fake_path')

    def test_load_config_only_repos(self):
        config_text = """
        api_key: 1234567abc
        github_webhook_secret: 12345abc
        meta_repo: mtreinish/qiskit-sandbox
        repos:
          - qiskit/qiskit-terra
          - qiskit/qiskit-ignis
        """
        mock_open = unittest.mock.mock_open(read_data=config_text)
        with unittest.mock.patch('qiskit_bot.config.open', mock_open):
            self.assertRaises(vol.MultipleInvalid, config.load_config,
                              'fake_path')
