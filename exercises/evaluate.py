#!/usr/bin/env python3
# =============================================================================
#     File: evaluate.py
#  Created: 2022-05-27 13:55
#   Author: Bernie Roesler
#
"""
Functions to evaluate infix and postfix expressions.
"""
# =============================================================================

from algs.basics import Stack, Queue


def evaluate_infix(a):
    """Evaluate a fully-parenthesized arithmetic infix expression using
    Dijkstra's Two-Stack Algorithm. See p 129.

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


# Exercise 1.3.10
def infix_to_postfix(a):
    """Convert an infix expression to a postfix expression.

    Parameters
    ----------
    a : str
        Space-delimited string of numbers, parentheses, and operators.

    Returns
    -------
    result : str
        A list of tokens corresponding to the postfix expression order.
    """
    q = Queue()
    OPS_D = list('+-*/^') + ['sqrt']
    s = Stack()
    for t in a.split():
        if t == '(':
            s.push(t)
        elif t in OPS_D:
            while s and s.peek() in OPS_D:
                q.enqueue(s.pop())
            s.push(t)
        elif t == ')':
            while s.peek() != '(':
                q.enqueue(s.pop())
            s.pop()  # discard the '(' value
        else:
            q.enqueue(t)  # an operand
    while s:
        q.enqueue(s.pop())
    return ' '.join(str(x) for x in q)


def evaluate_postfix(a):
    """Evaluate an arithmetic postfix expression.

    Parameters
    ----------
    a : str
        Space-delimited string of numbers and operators.

    Returns
    -------
    result : float
        The result of evaluating the expression.
    """
    OPS_D = list('+-*/^') + ['sqrt']
    s = Stack()
    for t in a.split():
        if t in OPS_D:
            # Token is the operator. Apply it to 1 or 2 values.
            v = s.pop()
            if t == '+':
                v = s.pop() + v
            elif t == '-':
                v = s.pop() - v
            elif t == '*':
                v = s.pop() * v
            elif t == '/':
                v = s.pop() / v
            elif t == '^':
                v = s.pop()**v
            elif t == 'sqrt':
                v = v**0.5    # unary operator, no second pop
            # Store the value computed
            s.push(v)
        else:
            s.push(float(t))
    return s.pop()


# Tests
if __name__ == '__main__':
    print(evaluate_infix('( 1 + ( ( 2 + 3 ) * ( 4 * 5 ) ) )'))  # == 101.0
    print(evaluate_infix('( ( 1 + sqrt ( 5.0 ) ) / 2.0 )'))     # == 1.6180339
    print(evaluate_infix('( 5 ^ 2 )'))  # 25.
    print(evaluate_postfix('1 2 3 + 4 5 * * +'))  # == 101.0
    p = infix_to_postfix('( 1 + ( ( 2 + 3 ) * ( 4 * 5 ) ) )')  # == '2 3 + 4 5 * * 1 +'
    print(p)
    print(evaluate_postfix(p))  # == 101.0

# =============================================================================
# =============================================================================
