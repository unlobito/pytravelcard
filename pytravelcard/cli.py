"""
This file intends to wrap the main library in a user-accessible CLI.
As a result, business logic shouldn't be contained here and unit testing should
primarily focus on the main library.
"""

import click
from . import PyTravelCard

from pprint import pprint

# Prepare Click
@click.group()
@click.pass_context
def cli(ctx):
    pass


# Commands
@cli.command('scan')
def scan():
    with PyTravelCard() as travelcard:
        name = travelcard.nfc_device_get_name()

        print("Found reader: " + name)

        card = travelcard.scan()

        pprint(vars(card))


# Time to blast off!
if __name__ == '__main__':
    cli()
