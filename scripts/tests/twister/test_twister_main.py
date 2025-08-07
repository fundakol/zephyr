# Copyright (c) 2025 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

import pytest
from twisterlib.twister_main import Twister


@pytest.fixture
def mock_test_plan():
    with (
        mock.patch("twisterlib.testplan.TestPlan.SAMPLE_FILENAME", 'test_sample_app.yaml'),
        mock.patch("twisterlib.testplan.TestPlan.TESTSUITE_FILENAME", 'test_data.yaml')
    ):
        yield


@pytest.mark.parametrize(
    "args, verbose",
    [
        ([], 0),
        (["-v"], 1),
        (["-vv"], 2),
    ],
    ids=("no-verbose", "verbose", "double-verbose")
)
def test_if_proper_verbose_is_selected(args, verbose):
    twister = Twister.create_instance(args)
    assert twister.options.verbose == verbose


@pytest.mark.parametrize(
    "args, log_level",
    [
        (["-ll", "INFO"], "INFO"),
        (["-ll", "DEBUG"], "DEBUG"),
    ],
    ids=("INFO", "DEBUG")
)
def test_if_proper_log_level_is_selected(args, log_level):
    twister = Twister.create_instance(args)
    assert twister.options.log_level == log_level


@pytest.mark.parametrize("log_level", ["INFO", "DEBUG"])
@pytest.mark.usefixtures("mock_test_plan")
def test_twister_collect_tests_with_different_log_level(
    tmp_path, testsuites_dir, capsys, log_level
):
    """Verify if changing log level in cli is reflected in twister logger."""
    out_dir = tmp_path / "twister-out"
    args = [
        "-T", os.path.join(testsuites_dir, "samples"),
        "-O", str(out_dir),
        "-ll", log_level,
        "--list-tests",
    ]
    twister = Twister.create_instance(args)
    assert twister.run() == 0
    captured = capsys.readouterr()

    assert "- sample_test.app" in captured.out
    matcher = pytest.LineMatcher(captured.err.split("\n"))
    matcher.fnmatch_lines(
        [
            "*INFO*Using Ninja..*",
            "*INFO*Using 'zephyr' toolchain.*",
        ]
    )
    expected_debug_logs = ["DEBUG*Calling cmake*"]
    if log_level == 'DEBUG':
        matcher.fnmatch_lines(
            expected_debug_logs
        )
    else:
        matcher.no_fnmatch_line(
            *expected_debug_logs
        )
