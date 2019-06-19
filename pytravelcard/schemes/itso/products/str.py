"""
Stored Travel Rights

TYP = 2
"""

from pytravelcard.schemes.itso.util import Util as util

from pprint import pprint

class STR():
    def __init__(self, ipe):
        self.ipe = ipe
        self.values = []

        self._parse_data()

        # Parse Value Record Data Groups
        if len(self.ipe.files) > 1:
            self._parse_value()

    def _parse_data(self):
        self.RemoveDate = util.byterange(self.ipe.data, 2, 1).uint
        self.ProductRetailer = util.byterange(self.ipe.data, 3, 2).hex
        self.TYP2Flags = util.byterange(self.ipe.data, 5, 1).hex
        self.Threshold = util.byterange(self.ipe.data, 6, 2).uint
        self.MaxValue2 = util.byterange(self.ipe.data, 10, 2).uint
        self.MaximumNegativeAmount = util.byterange(self.ipe.data, 12, 2).uint
        self.DepositAmount = util.byterange(self.ipe.data, 14, 2).uint
        self.StartDateAutoTopUp = util.en1545_DATE_from(util.byterange(self.ipe.data, 16, 1.75).uint)
        self.DepositMethodOfPayment = util.byterange(self.ipe.data, 19.5, 0.5)
        self.DepositCurrencyCode = util.byterange(self.ipe.data, 20, 0.5)
        self.DepositVATSalesTax = util.byterange(self.ipe.data, 20.5, 2).uint

    def _parse_value(self):
        for x in range(1, len(self.ipe.files)):
            file = self.ipe.files[x]
            VGBitmap = util.byterange(file, 0.75, 0.75)

            for y in range(0, VGBitmap[:-1].count(1)):
                record_start = 16 + 120*y
                record_end = record_start + 120

                record = self.ipe.files[x][:16] + self.ipe.files[x][record_start:record_end]

                value = STRValue(record)
                self.values.append(value)


class STRValue:
    def __init__(self, data):
        self.data = data

        self._parse_data()

    def _parse_data(self):
        self.TransactionType = util.en1545_EventTypeCode(util.byterange(self.data, 2, 0.5).uint)
        self.TransactionSequenceNumber = util.byterange(self.data, 2.5, 1.5).uint
        self.DateTimeStamp = util.en1545_DATETIME_from(util.byterange(self.data, 4, 3).uint)
        self.ISAMIDModifier = util.byterange(self.data, 7, 4).hex
        self.ActionSequenceNumber = util.byterange(self.data, 11, 1).uint
        self.Value = util.byterange(self.data, 12, 2).uint
        self.ValueCurrencyCode = util.byterange(self.data, 14, 0.5)
        self.CountJourneyLegs = util.byterange(self.data, 14.5, 0.5)
        self.CumulativeFare = util.byterange(self.data, 15, 1.625).uint
        self.TYP2ValueFlags = util.byterange(self.data, 16.625, 0.375)
