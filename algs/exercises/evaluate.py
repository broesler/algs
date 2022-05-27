#!/usr/bin/env python3
# =============================================================================
#     File: evaluate.py
#  Created: 2022-05-27 13:55
#   Author: Bernie Roesler
#
"""
Dijkstra's Two-Stack Algorithm for Expression Evaluation. See p 129.
"""
# =============================================================================

from algs.basics import Stack


def evaluate(a):
    """Evaluate a fully-parenthesized arithmetic infix expression.

    Parameters
    ----------
    a : str
        Space-delimited string of numbers, parentheses, and operators.

    Returns
    -------
    result : float
        The result of evaluating the expression.
    """
    OPS_D = list('+-*/^') + ['sqrt']
    ops = Stack()
    vals = Stack()
    for t in a.split():
        if t == '(':
            continue
        elif t in OPS_D:
            # Store operators until we hit a close parens
            ops.push(t)
        elif t == ')':
            # Get the operator and apply it to 1 or 2 values
            op = ops.pop()
            v = vals.pop()
            if op == '+':
                v = vals.pop() + v
            elif op == '-':
                v = vals.pop() - v
            elif op == '*':
                v = vals.pop() * v
            elif op == '/':
                v = vals.pop() / v
            elif op == '^':
                v = vals.pop()**v
            elif op == 'sqrt':
                v = v**0.5    # unary operator, no second pop
            # Store the value computed
            vals.push(v)
        else:
            vals.push(float(t))
    return vals.pop()


# Tests
if __name__ == '__main__':
    print(evaluate('( 1 + ( ( 2 + 3 ) * ( 4 * 5 ) ) )'))  # == 101.0
    print(evaluate('( ( 1 + sqrt ( 5.0 ) ) / 2.0 )'))     # == 1.6180339
    print(evaluate('( 5 ^ 2 )'))  # 25.

# =============================================================================
# =============================================================================
