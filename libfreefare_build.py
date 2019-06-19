from cffi import FFI
import os

ffibuilder = FFI()

ffibuilder.set_source("_freefare", None)

with open(os.path.join(os.path.dirname(__file__), "nfc.h.preprocessed")) as f:
    cdef = [n for n in f if not n.startswith('#')]

    ffibuilder.cdef("".join(cdef))

with open(os.path.join(os.path.dirname(__file__), "freefare.h.preprocessed")) as f:
    cdef = "".join([n for n in f if not n.startswith('#')])

    cdef = "typedef long int off_t;\n" + cdef
    cdef = "struct mifare_desfire_aid { uint8_t data[3]; };\n" + cdef

    ffibuilder.cdef(cdef)

if __name__ == "__main__":
    ffibuilder.compile(tmpdir="./pytravelcard/", verbose=True)
