"""
ITSO Shell Implementation
"""

from pprint import pprint

from pytravelcard.schemes.itso.util import Util as util

from enum import Enum


class Shell:
    TYPES = Enum('TYPES', 'COMPACT FULL')

    def __init__(self, shell_bits):
        self.shell_bits = shell_bits

        self._parse_shell()

    """
    Extract and expose all of the shell's parameters
    
    Reference:
    - ITSO TS 1000-2 section 4.1
    - ITSO TS 1000-10 section 3.7.4.4.3
    """
    def _parse_shell(self):
        self.shell_length = util.bitrange(self.shell_bits, (0, 7), (0, 2)).uint

        self.shell_bitmap = util.bitrange(self.shell_bits, (0, 1), (1, 4))
        self._parse_shell_bitmap()

        shell_format_revision = util.bitrange(self.shell_bits, (1, 3), (1, 0)).hex

        # Compact shells only contain four basic fields.
        if self.shell_bitmap_type == self.TYPES.COMPACT:
            FVC = util.bitrange(self.shell_bits, (2, 0), (2, 7)).hex
            return

        isrn_iin = util.bitrange(self.shell_bits, (2, 7), (4, 0))
        isrn_oid = util.bitrange(self.shell_bits, (5, 7), (6, 0))
        isrn_issn = util.bitrange(self.shell_bits, (7, 7), (10, 4))
        isrn_chd = util.bitrange(self.shell_bits, (10, 3), (10, 0))

        isrn = isrn_iin + isrn_oid + isrn_issn + isrn_chd

        self.isrn = util.bcd_digits(isrn.bytes)

        self.FVC = util.bitrange(self.shell_bits, (11, 7), (11, 0)).uint
        self.KSC = util.bitrange(self.shell_bits, (12, 7), (12, 0)).uint
        self.KVC = util.bitrange(self.shell_bits, (13, 7), (13, 0)).uint

        expiry_bitrange = util.bitrange(self.shell_bits, (14, 5), (15, 0))
        self.expiry = util.en1545_DATE_from(expiry_bitrange.uint)

        self.sector_size = util.bitrange(self.shell_bits, (16, 7), (16, 0)).uint
        self.max_sectors = util.bitrange(self.shell_bits, (17, 7), (17, 0)).uint
        self.psi = len('{0:b}'.format(self.max_sectors-1))
        self.max_directory_entries = util.bitrange(self.shell_bits, (18, 7), (18, 0)).uint
        self.sctl_size = util.bitrange(self.shell_bits, (19, 7), (19, 0)).uint

        if not self.shell_bitmap_mcrn:
            SECRC = util.bitrange(self.shell_bits, (22, 7), (23, 0))
        else:
            # The Multi-application CM reference is padded with 0x and ends
            # in a check digit. These aren't part of the reference number, so
            # let's remove them.
            mcrn = util.bitrange(self.shell_bits, (20, 7), (29, 0))
            mcrn.replace('0xf', '')
            self.mcrn = mcrn.hex[:-1]

            SECRC = util.bitrange(self.shell_bits, (30, 7), (31, 0))


    """
    Interpret the shell's bitmap and derive future expectations for data parsing
    
    Reference:
    - ITSO TS 1000-2 section 4.1.2
    """
    def _parse_shell_bitmap(self):
        if self.shell_bitmap.int == 0:
            self.shell_bitmap_type = self.TYPES.COMPACT
        elif self.shell_bitmap[5]:
            self.shell_bitmap_type = self.TYPES.FULL
            self.shell_bitmap_mcrn = self.shell_bitmap[4]
        else:
            raise TypeError

