# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .sale import *


def register():
    Pool.register(
        Sale,
        SaleLine,
        ProcessLinesSelect,
        module='sale_process_lines', type_='model')
    Pool.register(
        ProcessLines,
        module='sale_process_lines', type_='wizard')
