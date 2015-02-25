# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button

__all__ = ['Sale', 'SaleLine', 'ProcessLinesSelect', 'ProcessLines']
__metaclass__ = PoolMeta


class Sale:
    __name__ = 'sale.sale'

    pending_process = fields.Function(
        fields.Boolean('Pending to process'),
        'on_change_with_pending_process')

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        cls._buttons.update({
                'process_lines': {
                    'invisible': ~Eval('pending_process', False),
                    },
                })

    @fields.depends('lines', 'state')
    def on_change_with_pending_process(self, name=None):
        if self.state not in ('confirmed', 'processing'):
            return False
        if self.state == 'confirmed':
            return True
        return not all(l.processing for l in self.lines if l.type == 'line')

    @classmethod
    @ModelView.button_action('sale_process_lines.wizard_process_lines')
    def process_lines(cls, sales):
        pass

    @classmethod
    def do(cls, sales):
        pool = Pool()
        SaleLine = pool.get('sale.line')

        super(Sale, cls).do(sales)

        sale_lines = [l for s in sales for l in s.lines
            if l.type == 'line' and l.processing]
        SaleLine.write(sale_lines, {
                'processing': False,
                })


class SaleLine:
    __name__ = 'sale.line'

    processing = fields.Boolean('Processing', readonly=True)

    def get_invoice_line(self, invoice_type):
        if not self.processing:
            return []
        return super(SaleLine, self).get_invoice_line(invoice_type)

    def get_move(self, shipment_type):
        if not self.processing:
            return
        return super(SaleLine, self).get_move(shipment_type)

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default['processing'] = False
        return super(SaleLine, cls).copy(lines, default=default)


class ProcessLinesSelect(ModelView):
    'Process Lines Wizard - Select Lines'
    __name__ = 'sale.process.lines.select'

    sale = fields.Many2One('sale.sale', 'Sale', required=True, readonly=True)
    lines = fields.Many2Many('sale.line', None, None, 'Lines to process',
        domain=[
            ('sale', '=', Eval('sale', -1)),
            ('type', '=', 'line'),
            ('product', '!=', None),
            ('processing', '=', False),
            ], depends=['sale'])


class ProcessLines(Wizard):
    'Process Lines Wizard'
    __name__ = 'sale.process.lines'
    start_state = 'select'

    select = StateView('sale.process.lines.select',
        'sale_process_lines.process_lines_select_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Process _Lines', 'process_lines', 'tryton-ok',
                default=True),
            Button('Process _Order', 'process_order', 'tryton-ok'),
            ])
    process_lines = StateTransition()
    process_order = StateTransition()

    def default_select(self, fields):
        return {
            'sale': Transaction().context.get('active_id'),
            }

    def transition_process_lines(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')

        sale = self.select.sale
        if self.select.lines:
            SaleLine.write(self.select.lines, {
                    'processing': True,
                    })
            Sale.process([sale])
        return 'end'

    def transition_process_order(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')

        sale = self.select.sale
        sale_lines = [l for l in sale.lines
            if l.type == 'line' and not l.processing]
        if sale_lines:
            SaleLine.write(sale_lines, {
                    'processing': True,
                    })
            Sale.process([sale])
        return 'end'
