"""
Parent class for supported smartcard chipset technologies.

Don't directly use this, you should create a new class for each chipset that
inherits this one.
"""


class Target:
    def __init__(self, freefare, tag):
        self.freefare = freefare
        self.tag = tag
