#!/Users/bernardroesler/anaconda3/envs/insight/bin/python3
#==============================================================================
#     File: dup_test.py
#  Created: 2019-01-18 16:01
#   Author: Bernie Roesler
#
"""
  Description:
"""
#==============================================================================
# Python program to remove all adjacent duplicates from a string

def remove_recursive(string, last_removed):
    """Recursively removes adjacent duplicates from str and returns
    new string. las_removed is a pointer to last_removed character."""

    # If length of string is 1 or 0
    if len(string) == 0 or len(string) == 1:
        return string

    # Remove leftmost same characters and recur for remaining
    # string
    print(f'{string}, {last_removed}: ', end='')
    if string[0] == string[1]:
        last_removed = string[0]
        while len(string) > 1 and string[0] == string[1]:
            string = string[1:]
        string = string[1:]

        print('called from if')
        return remove_recursive(string, last_removed)

    # At this point, the first character is definiotely different
    # from its adjacent. Ignore first character and recursively
    # remove characters from remaining string
    print('called from rem_str')
    rem_str = remove_recursive(string[1:], last_removed)
    print('rem_str = ', rem_str)

    # Check if the first character of the rem_string matches
    # with the first character of the original string
    if len(rem_str) != 0 and rem_str[0] == string[0]:
        last_removed = string[0]
        return (rem_str[1:])

    # If remaining string becomes empty and last removed character
    # is same as first character of original string. This is needed
    # for a string like "acbbcddc"
    if len(rem_str) == 0 and last_removed == string[0]:
        return rem_str

    # If the two first characters of str and rem_str don't match,
    # append first character of str before the first character of
    # rem_str.
    print(f'{string}, {last_removed}: ')
    return string[0] + rem_str

def remove_dups(string):
    """Remove adjacent duplicates from string."""
    last_removed = chr(0)
    return remove_recursive(string, last_removed)

# Driver program
# string1 = "geeksforgeeks"
string1 = 'zznnMyyttT'
print(remove_dups(string1))
#==============================================================================
#==============================================================================
