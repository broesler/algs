#!/usr/bin/env python3
# =============================================================================
#     File: conftest.py
#  Created: 2026-06-15 15:16
#   Author: Bernie Roesler
# =============================================================================

"""Fixtures for graph tests."""

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'


# NOTE paths are relative to where pytest is run from
# See: <https://docs.pytest.org/en/6.2.x/customize.htmlinding-the-rootdir>
@pytest.fixture
def tinyCG(GraphType):
    return GraphType.fromfile(DATA_DIR / 'tinyCG.txt')


@pytest.fixture
def tinyG(GraphType):
    return GraphType.fromfile(DATA_DIR / 'tinyG.txt')


# =============================================================================
# =============================================================================
