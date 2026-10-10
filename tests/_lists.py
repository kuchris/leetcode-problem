"""Linked-list helpers for tests of ListNode-based solutions."""

from _loader import load_solution


class ListNode:
    """Stand-in for the ListNode that LeetCode injects via its preamble."""

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def build(values) -> ListNode | None:
    """Build a linked list from a sequence, returning its head."""
    head = None
    for value in reversed(list(values)):
        head = ListNode(value, head)
    return head


def to_list(head) -> list[int]:
    """Collect a linked list into a Python list."""
    values = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


def load_list_solution(filename):
    """Load a solution and give it a ListNode to construct dummy nodes with."""
    module = load_solution(filename)
    module.ListNode = ListNode
    return module
