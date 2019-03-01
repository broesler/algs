#!/home/broesler/anaconda3/envs/expo/bin/python3
#==============================================================================
#     File: stack.py
#  Created: 2019-02-08 17:23
#   Author: Bernie Roesler
#
"""
  Description: Implement a basic Stack data structure
"""
#==============================================================================

class Stack():
    """Implement a Stack data structure."""
    def __init__(self):
        self.items = []

    def is_empty(self):
        return not self.items

    def push(self, item):
        return self.items.append(item)

    def pop(self):
        return self.items.pop()

    def length(self):
        return len(self.items)

#==============================================================================
#==============================================================================
