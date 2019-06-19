"""
MIFARE DESFire implementation
"""

from pytravelcard.targets._target import Target
from pytravelcard._freefare import ffi
import pytravelcard.schemes as schemes

from bitstring import BitArray

class MifareDesfire(Target):
    def __init__(self, freefare, tag):
        super().__init__(freefare, tag)

        if self.freefare.freefare_get_tag_type(self.tag) != self.freefare.MIFARE_DESFIRE:
            raise TypeError

        res = self.freefare.mifare_desfire_connect(self.tag)
        if res < 0:
            raise TypeError

        self.find_shell()

    def __exit__(self):
        self.freefare.mifare_desfire_disconnect(self.tag)

    def get_applications(self):
        aids = ffi.new("MifareDESFireAID **")
        count = ffi.new("size_t *")

        res = self.freefare.mifare_desfire_get_application_ids(self.tag, aids, count)

        aid_list = []

        for x in range(0, count[0]):
            aid_buffer = ffi.buffer(aids[0][x].data, 3)
            aid = bytearray(aid_buffer[:])
            aid.reverse()

            aid_list.append(int(aid.hex(), 16))

        return aid_list

    def get_file(self, application, file):
        aid = self.freefare.mifare_desfire_aid_new(application)
        res = self.freefare.mifare_desfire_select_application(self.tag, aid)

        if res < 0:
            return False

        with ffi.new("uint8_t[256]") as data:
            bytes_received = self.freefare.mifare_desfire_read_data(self.tag, file, 0x00, 0, data)

            bit_buffer = ffi.buffer(data)
            bits = BitArray(bit_buffer[:bytes_received])

        return bits

    def find_shell(self):
        applications = self.get_applications()

        if 0xA00216 in applications:
            self.shell = self.find_itso_shell()
            self.directory = self.find_itso_directory(self.shell)


            self.entries = []
            for x in range(0, len(self.directory.entries)):
                entry = self.find_itso_ipe(self.directory.entries[x])

                if entry is not None:
                    self.entries.append(entry)

    def find_itso_shell(self):
        shell_bits = self.get_file(0xA00216, 0x0F)
        shell = schemes.itso.Shell(shell_bits)

        return shell

    def find_itso_directory(self, shell):
        directory_bits = self.get_file(0xA00216, 0x00)
        directory = schemes.itso.Directory(directory_bits, shell)

        return directory

    def find_itso_ipe(self, ipe_entry):
        if ipe_entry.typ == 0:
            return None

        ipe_files = []

        for sct_entry in ipe_entry.sct_chain:
            file_id = 15 - sct_entry
            file = self.get_file(0xA00216, file_id)

            ipe_files.append(file)

        ipe = schemes.itso.IPE(ipe_entry, ipe_files)

        return ipe

