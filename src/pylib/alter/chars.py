# -*- coding: utf-8 -*-

"""
    Character String Operation
"""

import hashlib
import random
import string

import regex as re


__all__ = (
    "str_rnd",
    "hash2s",
    "hash2b",
)


def str_rnd(
    number: int = 12, upper: bool = False, strong: bool = False, ultra: bool = False
) -> str:
    """generate random string"""
    seed = string.ascii_lowercase + string.digits
    if upper is True:
        seed = string.ascii_letters + string.digits
    if strong is True:
        seed = string.ascii_letters + string.digits + "@#$%"
    if ultra is True:
        seed = string.ascii_letters + string.digits + string.punctuation
    rnd = [random.choice(seed) for _ in range(number)]
    return "".join(rnd)


def hash2s(text: str) -> str:
    """generate hash string for text string"""
    middle = hashlib.md5(text.encode())
    return middle.hexdigest()


def hash2b(text: str) -> bytes:
    """generate hash bytes for text string"""
    middle = hashlib.md5(text.encode())
    return middle.digest()
