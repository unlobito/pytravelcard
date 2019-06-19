"""
ITSO Product Entity
"""

from pprint import pprint

from bitstring import BitArray
from pytravelcard.schemes.itso.util import Util as util

from pytravelcard.schemes.itso.products.str import STR
from pytravelcard.schemes.itso.products.journey import Journey
from pytravelcard.schemes.itso.products.id import ID

class IPEDirectoryEntry:
    def __init__(self, id: int, entry: BitArray, sct: dict, max_sectors: int):
        if entry.uint == 0:
            raise TypeError

        self.id = id
        self.entry = entry

        self.sct_chain = []

        self._parse_directory_entry()
        self._parse_sct_chain(sct, max_sectors)

    def _parse_directory_entry(self):
        self.oid_extension_flag = self.entry[0]
        self.oid = util.bitrange(self.entry, (0, 6), (1, 2)).uint
        self.typ = util.bitrange(self.entry, (1, 1), (2, 5)).uint
        self.ptyp = util.bitrange(self.entry, (2, 4), (2, 0)).uint
        self.vgp = self.entry[23]
        self.iiin = self.entry[24]

        expiry_bitrange = util.bitrange(self.entry, (3, 5), (4, 0))
        self.expiry = util.en1545_DATE_from(expiry_bitrange.uint)

    def _parse_sct_chain(self, sct: dict, max_sectors: int):
        current = self.id

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


class IPE:
    def __init__(self, ipe_entry: IPEDirectoryEntry, ipe_files: list):
        self.ipe_entry = ipe_entry
        self.files = ipe_files
        self.data = ipe_files[0]

        self._parse_ipe_headers()
        self._parse_ipe_data()

    def _parse_ipe_headers(self):
        self.length = self.data[0:6].uint
        self.bitmap = self.data[6:12]
        self.format_revision = self.data[12:16].uint

    def _parse_ipe_data(self):
        # Stored Travel Rights
        if self.ipe_entry.typ == 2:
            self.product = STR(self)

        # ITSO ID & entitlement
        if self.ipe_entry.typ == 16:
            self.product = ID(self)

        # Journey Ticket
        if self.ipe_entry.typ == 23:
            self.product = Journey(self)
