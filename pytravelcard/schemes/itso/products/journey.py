"""
Pre-defined Specific Journey Ticket,
with multi-ride and action list amendment capability options

TYP = 23
"""

from pytravelcard.schemes.itso.util import Util as util

class Journey():
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
        self.TYP23Flags = util.byterange(self.ipe.data, 5, 1).hex
        self.PassbackTime = util.byterange(self.ipe.data, 6.25, 0.75).uint
        self.IssueDate = util.en1545_DATE_from(util.byterange(self.ipe.data, 7.25, 1.75).uint)
        self.ValidityCode = util.byterange(self.ipe.data, 9, 0.625).uint
        self.ExpiryTime = util.byterange(self.ipe.data, 9.625, 1.375).uint
        self.Class = util.byterange(self.ipe.data, 11.625, 0.375).uint
        self.PartySizeAdult = util.byterange(self.ipe.data, 12, 1).uint
        self.PartySizeChild = util.byterange(self.ipe.data, 13, 1).uint
        self.PartySizeConcession = util.byterange(self.ipe.data, 14, 1).uint
        self.AmountPaidCurrencyCode = util.byterange(self.ipe.data, 15.5, 0.5).uint

        if self.ipe.format_revision == 1:
            self.AmountPaid = util.byterange(self.ipe.data, 16, 2).uint
            self.AmountPaidMethodOfPayment = util.byterange(self.ipe.data, 18, 0.5).uint
            self.AmountPaidVATSalesTax = util.byterange(self.ipe.data, 18.5, 1.5).uint
            self.PhotocardNumber = util.byterange(self.ipe.data, 20, 4)
            self.PromotionCode = util.byterange(self.ipe.data, 24, 1)
            self.ConcessionaryPassIssuerCostCentre = util.byterange(self.ipe.data, 25, 2)
            self.TYP23Mode = util.byterange(self.ipe.data, 27.5, 0.5)
            self.MaxTransfers = util.byterange(self.ipe.data, 28, 1).uint
            self.TimeLimit = util.byterange(self.ipe.data, 29, 1).uint
            self.ValueOfRideJourney = util.byterange(self.ipe.data, 30, 2).uint
            self.ValueOfRideJourneyCurrency = util.byterange(self.ipe.data, 32.5, 0.5)
            self.Origin1 = util.byterange(self.ipe.data, 33, 17)
            self.Destination1 = util.byterange(self.ipe.data, 50, 17)
            self.IIN = util.byterange(self.ipe.data, 67, 3)

        elif self.ipe.format_revision == 2:
            self.AmountPaid = util.byterange(self.ipe.data, 16, 2).uint
            self.AmountPaidMethodOfPayment = util.byterange(self.ipe.data, 18, 0.5).uint
            self.AmountPaidVATSalesTax = util.byterange(self.ipe.data, 18.5, 1.5).uint
            self.PhotocardNumber = util.byterange(self.ipe.data, 20, 4)
            self.PromotionCode = util.byterange(self.ipe.data, 24, 1)
            self.ConcessionaryPassIssuerCostCentre = util.byterange(self.ipe.data, 25, 2)
            self.TYP23Mode = util.byterange(self.ipe.data, 29.5, 0.5)
            self.MaxTransfers = util.byterange(self.ipe.data, 30, 1).uint
            self.TimeLimit = util.byterange(self.ipe.data, 31, 1).uint
            self.ValueOfRideJourney = util.byterange(self.ipe.data, 32, 2).uint
            self.ValueOfRideJourneyCurrency = util.byterange(self.ipe.data, 34.5, 0.5)
            self.RouteCode = util.byterange(self.ipe.data, 34.5, 0.5)
            self.Origin1 = util.byterange(self.ipe.data, 40, 17)
            self.Destination1 = util.byterange(self.ipe.data, 57, 17)
            self.IIN = util.byterange(self.ipe.data, 74, 3)

    def _parse_value(self):
        for x in range(1, len(self.ipe.files)):
            file = self.ipe.files[x]
            VGBitmap = util.byterange(file, 0.75, 0.75)

            for y in range(0, VGBitmap[:-1].count(1)):
                record_start = 16 + 120*y
                record_end = record_start + 120

                record = self.ipe.files[x][:16] + self.ipe.files[x][record_start:record_end]

                value = JourneyValue(record)
                self.values.append(value)


class JourneyValue:
    def __init__(self, data):
        self.data = data

        self._parse_data()

    def _parse_data(self):
        self.TransactionType = util.en1545_EventTypeCode(util.byterange(self.data, 2, 0.5).uint)
        self.TransactionSequenceNumber = util.byterange(self.data, 2.5, 1.5).uint
        self.DateTimeStamp = util.en1545_DATETIME_from(util.byterange(self.data, 4, 3).uint)
        self.ISAMIDModifier = util.byterange(self.data, 7, 4).hex
        self.ActionSequenceNumber = util.byterange(self.data, 11, 1).uint
        self.CountRemainingRidesJourney = util.byterange(self.data, 12, 1).uint
        self.CountTransfers = util.byterange(self.data, 13, 1).uint
        self.TYP23ValueFlags = util.byterange(self.data, 14, 1)
