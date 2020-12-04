# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import sale


def register():
    Pool.register(
        sale.Sale,
        sale.SaleLine,
        sale.ProcessLinesSelect,
        module='sale_process_lines', type_='model')
    Pool.register(
        sale.ProcessLines,
        module='sale_process_lines', type_='wizard')
