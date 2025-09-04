#!/usr/bin/env python3
# Copyright (c) 2024 Intel Corporation
#
# SPDX-License-Identifier: Apache-2.0
"""
Blackbox tests for twister's command line functions - simple does-error-out or not tests
"""

import os
import re
import sys
from unittest import mock

import pytest
# pylint: disable=no-name-in-module
from conftest import TEST_DATA, suite_filename_mock
from twisterlib.error import TwisterRuntimeError
from twisterlib.testplan import TestPlan
from twisterlib.twister_main import main as twister_main


class TestError:
    TESTDATA_1 = [
        (
            os.path.join(TEST_DATA, 'tests', 'dummy'),
            os.path.join('scripts', 'tests', 'twister_blackbox', 'test_data', 'tests',
                         'dummy', 'agnostic', 'group1', 'subgroup1',
                         'dummy.agnostic.group1.subgroup1'),
            None
        ),
        (
            None,
            'dummy.agnostic.group1.subgroup1',
            TwisterRuntimeError
        ),
        (
            os.path.join(TEST_DATA, 'tests', 'dummy'),
            'dummy.agnostic.group1.subgroup1',
            None
        )
    ]
    TESTDATA_2 = [
        (
            '',
            r'always_overflow.dummy SKIPPED \(RAM overflow\)'
        ),
        (
            '--overflow-as-errors',
            r'always_overflow.dummy ERROR Build failure \(build <zephyr>\)'
        )
    ]

    @pytest.mark.parametrize(
        'testroot, test, expected_exception',
        TESTDATA_1,
        ids=['valid', 'invalid', 'valid']
    )
    @mock.patch.object(TestPlan, 'TESTSUITE_FILENAME', suite_filename_mock)
    def test_test(self, out_path, testroot, test, expected_exception):
        test_platforms = ['qemu_x86', 'intel_adl_crb']
        args = []
        if testroot:
            args = ['-T', testroot]
        args += ['--detailed-test-id', '-i', '--outdir', out_path, '--test', test, '-y'] + \
               [val for pair in zip(
                   ['-p'] * len(test_platforms), test_platforms
               ) for val in pair]

        if expected_exception:
            with pytest.raises(expected_exception):
                twister_main(args)
        else:
            assert twister_main(args) == 0

    @pytest.mark.parametrize(
        'switch, expected',
        TESTDATA_2,
        ids=[
            'overflow skip',
            'overflow error',
        ],
    )

    @mock.patch.object(TestPlan, 'TESTSUITE_FILENAME', suite_filename_mock)
    def test_overflow_as_errors(self, capfd, out_path, switch, expected):
        path = os.path.join(TEST_DATA, 'tests', 'qemu_overflow')
        test_platforms = ['qemu_x86']
        args = ['--detailed-test-id', '--outdir', out_path, '-T', path, '-vv'] + \
               ['--build-only'] + \
               [val for pair in zip(
                   ['-p'] * len(test_platforms), test_platforms
               ) for val in pair]
        if switch:
            args += [switch]

        return_value = twister_main(args)

        out, err = capfd.readouterr()
        sys.stdout.write(out)
        sys.stderr.write(err)

        print(args)
        if switch:
            assert return_value == 1
        else:
            assert return_value == 0

        assert re.search(expected, err)
