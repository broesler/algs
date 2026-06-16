#!/usr/bin/env python3
# =============================================================================
#     File: conftest.py
#  Created: 2026-06-15 19:22
#   Author: Bernie Roesler
# =============================================================================

"""Fixtures for all algorithms tests."""

from pathlib import Path

import pytest


@pytest.fixture
def data_dir():
    return Path(__file__).parents[1] / 'data'


# =============================================================================
# =============================================================================
