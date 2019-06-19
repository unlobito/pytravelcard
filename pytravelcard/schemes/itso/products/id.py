"""
ITSO shell personalisation

TYP = 16
"""

from pytravelcard.schemes.itso.util import Util as util

class ID():
    def __init__(self, ipe):
        self.ipe = ipe
        self.values = []

        self._parse_data()

    def _parse_data(self):
        self.RemoveDate = util.byterange(self.ipe.data, 2, 1).uint
        self.ConcessionaryPassIssuerCostCentre = util.byterange(self.ipe.data, 3, 2).hex
        self.IDFlags = util.byterange(self.ipe.data, 5, 1).hex
        self.RoundingFlagsEnable = util.byterange(self.ipe.data, 6, 0.125).bin
        self.PassbackTime = util.byterange(self.ipe.data, 6.25, 0.75).uint
        self.DateOfBirth = util.byterange(self.ipe.data, 7, 4, True)
        self.Language = util.byterange(self.ipe.data, 11, 1).uint
        self.HolderID = util.byterange(self.ipe.data, 11.625, 0.375).uint
        self.RoundingFlag = util.byterange(self.ipe.data, 16, 0.125).bin
        self.RoundingValueFlag = util.byterange(self.ipe.data, 16.13, 0.125).bin
        self.EntitlementExpiryDate = util.en1545_DATE_from(util.byterange(self.ipe.data, 16.25, 1.75).uint)
        self.DepositMethodOfPayment = util.byterange(self.ipe.data, 18, 0.5).uint

        self.DepositVATSalesTax = util.byterange(self.ipe.data, 18.5, 1.5).uint
        self.ShellDepositMethodOfPayment = util.byterange(self.ipe.data, 20, 0.5).uint
        self.ShellDepositVATSalesTax = util.byterange(self.ipe.data, 20.5, 1.5).uint
        self.DepositCurrencyCode = util.byterange(self.ipe.data, 22, 0.5).uint
        self.ShellDepositCurrencyCode = util.byterange(self.ipe.data, 22.5, 0.5).uint
        self.DepositAmount = util.byterange(self.ipe.data, 23, 2).uint
        self.ShellDeposit = util.byterange(self.ipe.data, 25, 2).uint
        self.EntitlementCode = util.byterange(self.ipe.data, 27, 1).uint
        self.ConcessionaryClass = util.byterange(self.ipe.data, 28, 1).uint
        self.SecondaryHolderID = util.byterange(self.ipe.data, 29, 4).uint

        self.ForenameLength = util.byterange(self.ipe.data, 33, 1).uint
        self.Forename = util.byterange(self.ipe.data, 34, self.ForenameLength).bytes.decode("ascii")

        surname_position = 34 + self.ForenameLength
        self.SurnameLength = util.byterange(self.ipe.data, surname_position, 1).uint
        self.Surname = util.byterange(self.ipe.data, surname_position+1, self.SurnameLength)

        ending_position = surname_position + self.SurnameLength
        self.HalfDayOfWeek = util.byterange(self.ipe.data, ending_position, 2)
        self.ValidAtOrFrom = util.byterange(self.ipe.data, ending_position+2, 17)
        self.ValidTo = util.byterange(self.ipe.data, ending_position+36, 17)
        self.IIN = util.byterange(self.ipe.data, ending_position+53, 3)