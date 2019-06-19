"""
Generic smartcard management. Technology specific communications / parsing
should be delegated to their own files.

Responsible for marshalling data between libfreefare/libnfc and Python
"""

from pprint import pprint

import ctypes.util
from ._freefare import ffi

import pytravelcard.targets as targets


class PyTravelCard:
    """
    Establish a libnfc instance and prepare a context for it
    """
    def __enter__(self):
        self.freefare = ffi.dlopen(ctypes.util.find_library("libfreefare"))

        self.context = ffi.new("nfc_context **")

        self.freefare.nfc_init(self.context)

        if self.context[0] is None:
            pprint("malloc failed")
            exit()

        self.device = self.freefare.nfc_open(self.context[0], ffi.NULL)

        if self.device == ffi.NULL:
            pprint("Failed to initialise NFC device")
            exit()

        self.freefare.nfc_initiator_init(self.device)

        return self

    """
    Clean up freefare instance & context
    """
    def __exit__(self, *args):
        self.freefare.nfc_close(self.device)
        self.freefare.nfc_exit(self.context[0])

    def nfc_device_get_name(self):
        name = self.freefare.nfc_device_get_name(self.device)
        return ffi.string(name).decode("UTF+8")

    """
    Scan for an available smartcard. If one is found, it will be probed for a
    recognised shell.

    :returns pytravelcard.smartcard: object describing the recognised smartcard.
    :raises pytravelcard.error.nfcTimeoutError:
    """
    def scan(self):
        tags = self.freefare.freefare_get_tags(self.device)

        if not tags[0]:
            pprint("Failed to find any tags")
            exit()

        if ffi.typeof(tags[1]) is ffi.typeof("FreefareTag*"):
            pprint("Found more than one tag")
            exit()

        tag = tags[0]
        tag_type = self.freefare.freefare_get_tag_type(tag)

        card = None

        if tag_type == self.freefare.MIFARE_CLASSIC_1K:
            pprint("Found card: mfclasic1k")
        elif tag_type == self.freefare.MIFARE_CLASSIC_4K:
            card = targets.MifareClassic4k(self.freefare, tag)
        elif tag_type == self.freefare.MIFARE_DESFIRE:
            card = targets.MifareDesfire(self.freefare, tag)
        elif tag_type == self.freefare.MIFARE_ULTRALIGHT:
            pprint("Found card: mfultralight")
        elif tag_type == self.freefare.MIFARE_ULTRALIGHT_C:
            pprint("Found card: mfultralightc")
        elif tag_type == self.freefare.NTAG_21x:
            pprint("Found card: ntag21x")
        else:
            pprint("Unrecognised card type")

        return card
