"""
Luferov Victor <lyferov@yandex.ru>

Fuzzy Terms
"""

from .mf import MembershipFunction


class Term:
    """
    Fuzzy term
    """

    def __init__(self, name: str, mf: MembershipFunction):
        self.name: str = name
        self.mf: MembershipFunction = mf
