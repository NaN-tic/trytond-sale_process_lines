===========================
Sale Process Lines Scenario
===========================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Install product_cost_plan Module::

    >>> config = activate_modules('sale_process_lines')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create sale user::

    >>> User = Model.get('res.user')
    >>> Group = Model.get('res.group')
    >>> sale_user = User()
    >>> sale_user.name = 'Sale'
    >>> sale_user.login = 'sale'
    >>> sale_user.main_company = company
    >>> sale_group, = Group.find([('name', '=', 'Sales')])
    >>> sale_user.groups.append(sale_group)
    >>> stock_group, = Group.find([('name', '=', 'Stock')])
    >>> sale_user.groups.append(stock_group)
    >>> account_group, = Group.find([('name', '=', 'Account')])
    >>> sale_user.groups.append(account_group)
    >>> sale_user.save()

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> payable = accounts['payable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> account_tax = accounts['tax']
    >>> account_cash = accounts['cash']

    >>> Journal = Model.get('account.journal')
    >>> cash_journal, = Journal.find([('type', '=', 'cash')])
    >>> cash_journal.credit_account = account_cash
    >>> cash_journal.debit_account = account_cash
    >>> cash_journal.save()

Create parties::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.purchasable = True
    >>> template.salable = True
    >>> template.list_price = Decimal('10')
    >>> template.cost_price = Decimal('5')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> product.template = template
    >>> product.save()

    >>> service = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'service'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.salable = True
    >>> template.list_price = Decimal('30')
    >>> template.cost_price = Decimal('10')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.save()
    >>> service.template = template
    >>> service.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create an Inventory::

    >>> config.user = sale_user.id
    >>> Inventory = Model.get('stock.inventory')
    >>> InventoryLine = Model.get('stock.inventory.line')
    >>> Location = Model.get('stock.location')
    >>> storage, = Location.find([
    ...         ('code', '=', 'STO'),
    ...         ])
    >>> inventory = Inventory()
    >>> inventory.location = storage
    >>> inventory.save()
    >>> inventory_line = InventoryLine(product=product, inventory=inventory)
    >>> inventory_line.quantity = 100.0
    >>> inventory_line.expected_quantity = 0.0
    >>> inventory.save()
    >>> inventory_line.save()
    >>> Inventory.confirm([inventory.id], config.context)
    >>> inventory.state
    u'done'

Sale 5 products::

    >>> config.user = sale_user.id
    >>> Sale = Model.get('sale.sale')
    >>> SaleLine = Model.get('sale.line')
    >>> sale = Sale()
    >>> sale.party = customer
    >>> sale.payment_term = payment_term
    >>> sale.invoice_method = 'order'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = 2.0
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.type = 'comment'
    >>> sale_line.description = 'Comment'
    >>> sale_line = SaleLine()
    >>> sale.lines.append(sale_line)
    >>> sale_line.product = product
    >>> sale_line.quantity = 3.0
    >>> sale.save()
    >>> Sale.quote([sale.id], config.context)
    >>> Sale.confirm([sale.id], config.context)

Process first line::

    >>> process_lines = Wizard('sale.process.lines', [sale])
    >>> process_lines.form.lines.append(SaleLine(sale.lines[0].id))
    >>> process_lines.execute('process_lines')
    >>> sale.reload()
    >>> sale.state
    u'processing'
    >>> len(sale.shipments), len(sale.shipment_returns), len(sale.invoices)
    (1, 0, 1)
    >>> sale.lines[0].processing and bool(sale.lines[0].moves)
    True
    >>> any(l.processing for l in sale.lines[1:])
    False
    >>> sale.pending_process
    True

Validate Shipment::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment, = sale.shipments
    >>> ShipmentOut.assign_try([shipment.id], config.context)
    True
    >>> ShipmentOut.pack([shipment.id], config.context)
    >>> ShipmentOut.done([shipment.id], config.context)

Post and pay invoice::

    >>> Invoice = Model.get('account.invoice')
    >>> invoice, = sale.invoices
    >>> invoice.click('post')
    >>> pay = Wizard('account.invoice.pay', [invoice])
    >>> pay.form.journal = cash_journal
    >>> pay.execute('choice')
    >>> invoice.reload()
    >>> invoice.state
    u'paid'

Sale is still processing::

    >>> sale.reload()
    >>> sale.state
    u'processing'

Process the pending lines::

    >>> process_lines = Wizard('sale.process.lines', [sale])
    >>> process_lines.execute('process_order')
    >>> sale.reload()
    >>> sale.state
    u'processing'
    >>> len(sale.shipments), len(sale.shipment_returns), len(sale.invoices)
    (2, 0, 2)
    >>> all((l.processing and l.moves) for l in sale.lines if l.type == 'line')
    True

Validate pending Shipment::

    >>> shipment, = [s for s in sale.shipments if s.state != 'done']
    >>> ShipmentOut.assign_try([shipment.id], config.context)
    True
    >>> ShipmentOut.pack([shipment.id], config.context)
    >>> ShipmentOut.done([shipment.id], config.context)

Post and pay pending invoice::

    >>> invoice, = [i for i in sale.invoices if i.state != 'paid']
    >>> invoice.click('post')
    >>> pay = Wizard('account.invoice.pay', [invoice])
    >>> pay.form.journal = cash_journal
    >>> pay.execute('choice')
    >>> invoice.reload()
    >>> invoice.state
    u'paid'

Sale is done::

    >>> sale.reload()
    >>> sale.state
    u'done'
