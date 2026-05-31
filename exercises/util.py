#!/usr/bin/env python3
# =============================================================================
#     File: util.py
#  Created: 2022-06-07 11:16
#   Author: Bernie Roesler
# =============================================================================

"""Utility functions used in exercises."""


def count_lines(fp):
    """Scan through file to count the number of lines."""
    num_lines = sum(1 for _ in fp)
    fp.seek(0)  # rewind file
    return num_lines


# =============================================================================
# =============================================================================
