#!/usr/bin/env python3
# Copyright (c) 2024 Intel Corporation
#
# SPDX-License-Identifier: Apache-2.0
"""
Blackbox tests for twister's command line functions related to the shuffling of the test order.
"""

from unittest import mock
import os
import pytest
import json

# pylint: disable=no-name-in-module
from conftest import TEST_DATA, suite_filename_mock
from twisterlib.testplan import TestPlan
from twisterlib.twister_main import main as twister_main


class TestShuffle:

    @pytest.mark.parametrize(
        'seed, ratio, expected_order',
        [
            ('123', '1/2', ['dummy.device.group', 'dummy.agnostic.group1.subgroup2']),
            ('123', '2/2', ['dummy.agnostic.group2', 'dummy.agnostic.group1.subgroup1']),
            ('321', '1/2', ['dummy.agnostic.group2', 'dummy.agnostic.group1.subgroup2']),
            ('321', '2/2', ['dummy.device.group', 'dummy.agnostic.group1.subgroup1']),
            ('123', '1/3', ['dummy.device.group', 'dummy.agnostic.group1.subgroup2']),
            ('123', '2/3', ['dummy.agnostic.group2']),
            ('123', '3/3', ['dummy.agnostic.group1.subgroup1']),
            ('321', '1/3', ['dummy.agnostic.group2', 'dummy.agnostic.group1.subgroup2']),
            ('321', '2/3', ['dummy.device.group']),
            ('321', '3/3', ['dummy.agnostic.group1.subgroup1'])
        ],
        ids=['first half, 123', 'second half, 123', 'first half, 321', 'second half, 321',
             'first third, 123', 'middle third, 123', 'last third, 123',
             'first third, 321', 'middle third, 321', 'last third, 321'
             ]
    )
    @mock.patch.object(TestPlan, 'TESTSUITE_FILENAME', suite_filename_mock)
    def test_shuffle_tests(self, out_path, seed, ratio, expected_order):
        test_platforms = ['qemu_x86', 'intel_adl_crb']
        path = os.path.join(TEST_DATA, 'tests', 'dummy')
        args = ['-i', '--outdir', out_path, '-T', path, '-y'] + \
               ['--shuffle-tests', '--shuffle-tests-seed', seed] + \
               ['--subset', ratio] + \
               [val for pair in zip(
                   ['-p'] * len(test_platforms), test_platforms
               ) for val in pair]

        return_value = twister_main(args)

        with open(os.path.join(out_path, 'testplan.json')) as f:
            j = json.load(f)

        testsuites = [os.path.basename(ts['name']) for ts in j['testsuites']]

        assert testsuites == expected_order

        assert return_value == 0
