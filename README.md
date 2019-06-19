# pytravelcard
python tools for interacting with ITSO-compliant smartcards

## Supported ITSO Environments
### Chipsets
* MIFARE Classic 4k
* MIFARE DESFire

### Products
* TYP2 - Stored Travel Rights
* TYP16 - ITSO shell personalisation
* TYP23 - Pre-defined Specific Journey Ticket

## System Requirements
nfc-tools [libfreefare](https://github.com/nfc-tools/libfreefare) must be
installed. A [supported NFC device](http://nfc-tools.org/index.php/Devices_compatibility_matrix)
should also be connected.

## Development
### Packaging
Checkout the repository and create a virtualenv using your preferred tooling.
Next, create an ["editable" install](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs)
for the module through pip.

```
$ pip install --editable=.
```

You will now be able to run `pytravelcard` from the command line and Python will
execute your local codebase. 

### cffi bindings
pytravelcard calls native libraries through the
[C Foreign Function Interface for Python](https://cffi.readthedocs.io/en/latest/).
When either of these libraries are updated, the cffi bindings should be rebuilt
to facilitate access to new API calls.

After checking out [libfreefare](https://github.com/nfc-tools/libfreefare) and
[libnfc](https://github.com/nfc-tools/libnfc) in the project directory, run `make`
and the `libfreefare_build.py` scripts to prepare and compile the native bindings.