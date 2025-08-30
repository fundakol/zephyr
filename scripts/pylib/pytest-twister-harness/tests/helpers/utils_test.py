# Copyright (c) 2025 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: Apache-2.0

import textwrap

import pytest
from twister_harness.helpers.utils import match_lines, match_no_lines

OUTPUT_LINES = textwrap.dedent("""\
    The Zen of Python, by Tim Peters
    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.\
""").split('\n')


CHECK_LINES = textwrap.dedent("""\
    Although never is often better than *right* now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!\
""").split('\n')


@pytest.mark.parametrize(
    "lines",
    [
        OUTPUT_LINES[0:1],
        OUTPUT_LINES[3:5],
        OUTPUT_LINES[-1:],
        [OUTPUT_LINES[-1][2:-2]],  # check partial of a text
    ],
)
def test_match_lines_positive(lines):
    match_lines(OUTPUT_LINES, lines)


@pytest.mark.parametrize(
    "lines", [CHECK_LINES[0:1], CHECK_LINES[1:3], CHECK_LINES[-1:], [CHECK_LINES[-1][2:-2]]]
)
def test_match_lines_negative(lines):
    with pytest.raises(AssertionError):
        match_lines(OUTPUT_LINES, lines)


@pytest.mark.parametrize("lines", [OUTPUT_LINES[0:1], OUTPUT_LINES[1:3], OUTPUT_LINES[-1:]])
def test_match_no_lines_negative(lines):
    with pytest.raises(AssertionError):
        match_no_lines(OUTPUT_LINES, lines)


@pytest.mark.parametrize(
    "lines",
    [
        CHECK_LINES[0:1],
        CHECK_LINES[3:5],
        CHECK_LINES[-1:],
    ],
)
def test_match_no_lines_positive(lines):
    match_no_lines(OUTPUT_LINES, lines)
