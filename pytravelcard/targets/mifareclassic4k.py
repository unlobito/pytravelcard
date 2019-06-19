"""
MIFARE Classic 4K implementation
"""

from pytravelcard.targets._target import Target
from pytravelcard._freefare import ffi
import pytravelcard.schemes as schemes

from bitstring import BitArray


class MifareClassic4k(Target):
    def __init__(self, freefare, tag):
        super().__init__(freefare, tag)

        if self.freefare.freefare_get_tag_type(self.tag) != self.freefare.MIFARE_CLASSIC_4K:
            raise TypeError

        res = self.freefare.mifare_classic_connect(self.tag)
        if res != 0:
            raise TypeError

        self.find_shell()

    def __exit__(self):
        self.freefare.mifare_classic_disconnect(self.tag)
        self.freefare = None
        self.tag = None

    def find_shell(self):
        self.shell = self.find_itso_shell()
        self.directory = self.find_itso_directory(self.shell)

        self.entries = []
        for x in range(0, len(self.directory.entries)):
            entry = self.find_itso_ipe(self.directory.entries[x])

            if entry is not None:
                self.entries.append(entry)

    def get_itso_sector(self, sector):
        mifare_keys = [
            [0x70, 0x32, 0x65, 0x49, 0x73, 0x50],
            [0x13, 0x06, 0x62, 0x24, 0x02, 0x00],
            [0x5e, 0x25, 0xc4, 0x99, 0x0a, 0xa9],
            [0x42, 0x45, 0x4c, 0x4c, 0x41, 0x47],
            [0x73, 0x51, 0x75, 0x69, 0x64, 0x21],

            [0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
            [0xd3, 0xf7, 0xd3, 0xf7, 0xd3, 0xf7],
            [0xa0, 0xa1, 0xa2, 0xa3, 0xa4, 0xa5],
            [0xb0, 0xb1, 0xb2, 0xb3, 0xb4, 0xb5],
            [0x4d, 0x3a, 0x99, 0xc3, 0x51, 0xdd],
            [0x1a, 0x98, 0x2c, 0x7e, 0x45, 0x9a],
            [0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff],
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        ]

        block = self.freefare.mifare_classic_sector_first_block(sector)
        length = self.freefare.mifare_classic_sector_block_count(sector)

        for key_bytes in mifare_keys:
            res = self.freefare.mifare_classic_connect(self.tag)

            key = ffi.new("MifareClassicKey", bytes(key_bytes))

            auth = self.freefare.mifare_classic_authenticate(self.tag, block, key, self.freefare.MFC_KEY_A)

            if auth == 0:
                break

        if auth != 0:
            return False

        bits = BitArray()

        for x in range(block, block+length):
            data = ffi.new("MifareClassicBlock *")
            self.freefare.mifare_classic_read(self.tag, x, data)

            buffer = ffi.buffer(data[0])
            bits += BitArray(buffer[:])

        return bits

    def find_itso_shell(self):
        key = ffi.new("MifareClassicKey", bytes([0x70, 0x32, 0x65, 0x49, 0x73, 0x50]))

        block = self.freefare.mifare_classic_sector_first_block(16)

        auth = self.freefare.mifare_classic_authenticate(self.tag, block, key, self.freefare.MFC_KEY_A)

        if auth != 0:
            return False

        shell_bits = BitArray()

        # Block 0 is always 0x00, per ITSO TS 1000-10 4.4, so we skip over it
        for x in range(block+1, block+3):
            data = ffi.new("MifareClassicBlock *")
            self.freefare.mifare_classic_read(self.tag, x, data)

            shell_buffer = ffi.buffer(data[0])
            shell_bits += BitArray(shell_buffer[:])

        shell = schemes.itso.Shell(shell_bits)

        return shell

    def find_itso_directory(self, shell):
        directory_bits = self.get_itso_sector(39)

        directory = schemes.itso.Directory(directory_bits, shell)

        return directory

    def find_itso_ipe(self, ipe_entry):
        if ipe_entry.typ == 0:
            return None

        ipe_files = []

        for sct_entry in ipe_entry.sct_chain:
            if sct_entry == 1:
                file_id = 1
            elif 2 <= sct_entry <= 13:
                file_id = 18 - sct_entry
            elif 14 <= sct_entry <= 27:
                file_id = sct_entry - 12
            elif 28 <= sct_entry <= 34:
                file_id = sct_entry - 3
            elif 35 <= sct_entry <= 37:
                file_id = sct_entry + 1

            file = self.get_itso_sector(file_id)

            if file is not False:
                ipe_files.append(file)

        if len(ipe_files) == 0:
            return None

        ipe = schemes.itso.IPE(ipe_entry, ipe_files)

        return ipe


