#!/usr/bin/env python3
# =============================================================================
#     File: helpers.py
#  Created: 2021-03-09 19:37
#   Author: Bernie Roesler
#
"""
  Description: Helper functions used in testing.
"""
# =============================================================================

# Define test counts
tests = fails = 0

def should_be(a, b, name=None, verbose=False):
    """Test a condition."""
    global tests, fails
    tests += 1
    try:
        assert a == b
        if verbose:
            print(f"[{name}]: Got: {a}, Expected: {b}")
    except AssertionError as e:
        fails += 1
        print(f"     Got: {a}\nExpected: {b}")
        raise e


def err_test(container, op, *args, err_type=IndexError):
    """Test for raising a given error type.

    Parameters
    ----------
    container : list-like container data type instance
        A class instance to be tested.
    op : str
        attribute name of method to test
    *args : list
        arguments to `op`.
    err_type : Exception, optional
        error type that object is expected to raise

    Raises
    ------
    Exception
        If error raised is not of type `err_type`.
    """
    global tests, fails
    tests += 1
    try:
        getattr(container, op)(*args)  # call the method
    except err_type:
        return
    except Exception as err:
        fails += 1
        print(f"Raised: {repr(err)}, Expected: {err_type}")
        raise err
    else:
        fails += 1
        print(f"No error raised! Expected: {err_type}")
        raise

# =============================================================================
# =============================================================================
