"""
ITSO Directory Data Group Implementation
"""

from pprint import pprint

from pytravelcard.schemes.itso.util import Util as util
from pytravelcard.schemes.itso.ipe import *

from enum import Enum


class Directory:
    def __init__(self, directory_bits, shell):
        self.directory_bits = directory_bits
        self.shell = shell
        self.entries = []
        self.sct = {}

        self._parse_directory()

    """
    Extract and expose all of the Directory Data Group’s parameters

    Reference:
    - ITSO TS 1000-2 section 5.1
    """
    def _parse_directory(self):
        self.directory_bitmap = util.bitrange(self.directory_bits, (0, 1), (1, 4))
        self._parse_directory_bitmap()

        directory_format_revision = util.bitrange(self.directory_bits, (1, 3), (1, 0))

        # Sector Chain Table
        for x in range(0, self.shell.max_sectors-3):
            position = (16 + 5*8*self.shell.max_directory_entries) + self.shell.psi * x

            entry_bits = self.directory_bits[position:position+self.shell.psi].uint

            self.sct[x+1] = entry_bits

        # Directory Entries
        for x in range(1, self.shell.max_directory_entries):
            position = 16 + 5*8*x

            entry_bits = self.directory_bits[position:position+40]

            # Skip entry empties
            if entry_bits.uint == 0:
                continue

            entry = IPEDirectoryEntry(x, entry_bits, self.sct, self.shell.max_sectors)
            self.entries.append(entry)

        # Cyclic Log
        log_location = (16 + 5 * 8 * self.shell.max_directory_entries)
        log = self.directory_bits[log_location:log_location + 40]
        self.log = LogDirectoryEntry(log, self.sct, self.shell.max_sectors)

        sequence_location = (16 + 5*8*self.shell.max_directory_entries) + self.shell.sctl_size*8
        self.sequence = self.directory_bits[sequence_location:sequence_location+8].uint
        self.kid = self.directory_bits[sequence_location+8:sequence_location+12]
        self.shell_iteration = self.directory_bits[sequence_location + 12:sequence_location + 16].uint
        self.isamid = self.directory_bits[sequence_location + 16:sequence_location + 48]

    """
    Interpret the DDG's bitmap and derive future expectations for data parsing

    Reference:
    - ITSO TS 1000-2 section 5.1.2
    """

    def _parse_directory_bitmap(self):
        self.shell_blocked = self.directory_bitmap[5]
        self.has_log_entry = self.directory_bitmap[4]


class LogDirectoryEntry:
    def __init__(self, entry, sct, max_sectors):
        self.entry = entry

        self.sct_chain = []

        self._parse_entry()
        self._parse_sct_chain(sct, max_sectors)

    def _parse_entry(self):
        self.normal = self.entry[0]
        self.pointer = self.entry[1:6].uint
        self.direction = self.entry[6:7].uint
        self.timestamp = util.en1545_DATE_from(self.entry[8:16].uint)
        self.offset = self.entry[32:33]
        self.passback = self.entry[33:39].uint

    def _parse_sct_chain(self, sct: dict, max_sectors: int):
        current = self.pointer

        while True:
            self.sct_chain.append(current)

            # Terminating chain, sector is unallocated
            if sct[current] == 0:
                break

            # Terminating chain, unused IPE
            if sct[current] == current:
                break

            # Terminating chain, product is blocked
            if sct[current] == max_sectors-1:
                break

            # Terminating chain, product is unblocked
            if sct[current] == max_sectors-2:
                break

            # If we've made it this far, this entry is continuing a chain
            current = sct[current]
