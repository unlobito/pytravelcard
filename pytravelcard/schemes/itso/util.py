from datetime import date, datetime, timedelta
from enum import IntEnum

from pprint import pprint


class Util:
    @staticmethod
    def bitrange(bitarray, start_range, end_range, bcd=False):
        start = int((start_range[0] * 8) + (8 - start_range[1]) - 1)  # zero-indexed
        end = int((end_range[0] * 8) + (8 - end_range[1]))

        value = bitarray[start:end]

        if not bcd:
            return value
        else:
            return Util.bcd_digits(value.tobytes())

    @staticmethod
    def byterange(bitarray, start_byte, length, bcd=False):
        start = int(start_byte * 8)
        end = int(start + (length * 8))

        value = bitarray[start:end]

        if not bcd:
            return value
        else:
            return Util.bcd_digits(value.tobytes())

    # https://stackoverflow.com/a/11669177
    @staticmethod
    def bcd_digits(chars):
        value = ''
        view = memoryview(chars)

        for char in view:
            for val in (char >> 4, char & 0xF):
                if val == 0xF:
                    return
                value = value + str(val)

        return value

    @staticmethod
    def en1545_DATE_from(source):
        EPOCH = date(year=1997, month=1, day=1)

        parsed = EPOCH + timedelta(days=source)

        return parsed

    @staticmethod
    def en1545_DATE_to(source):
        EPOCH = date(year=1997, month=1, day=1)

        parsed = (source - EPOCH).days

        return parsed

    @staticmethod
    def en1545_DATETIME_from(source):
        EPOCH = datetime(year=1997, month=1, day=1)

        parsed = EPOCH + timedelta(minutes=source)

        return parsed

    en1545_EventTypeCode = IntEnum(value='EventTypeCode', names=[
        'not_specified',
        'sale',
        'validation_outward_journey_if_return_ticket',
        'undo_previous_event_without_refund',
        'str_load',
        'str_autoload',
        'validation_return_journey',
        'str_debit',
        'exchange',
        'redeem_loyalty_points',
        'undo_previous_event_with_refund',
        'check_in',
        'check_out',
        'activate_stored_ticket',
        'record_of_multiple_leg_journey',
        'cta_payment_received',
        'check_in_transfer',
        'be_in_transfer',
        'user_modification',
        'consumed',
        'marked_as_blocked',
        'undo_blocking',
        'be_in',
        'be_out',
        'interruption',
        'refund_authorised',
        'inspection',
        'in_out',
        'undo_validation',
        'networkIdSpecific1'
    ], start=0)
