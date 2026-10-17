from odoo import _, api, fields, models, Command
from collections import defaultdict

class StockMove(models.Model):
    _inherit = 'stock.move'

    repair_product_line_type = fields.Selection([
        ('service', 'Service'),
        ('part', 'Part'),
    ], 'Type', store=True, index=True, required=False)

    domain_ids = fields.Char(string="Domain Ids")
    product_id = fields.Many2one(
        'product.product',
        check_company=True,
        index=True,
        required=True,
        domain="[]"
    )

    # Pricing fields
    currency_id = fields.Many2one(
        related='repair_id.currency_id',
        depends=['repair_id.currency_id'],
        store=True, precompute=True)

    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)

    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True)

    discount = fields.Float(
        string="Discount (%)",
        digits='Discount',
        store=True, readonly=False)

    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount',
        store=True, precompute=True)
    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',
        store=True, precompute=True)
    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        store=True, precompute=True)

    def _reset_price_unit(self):
        self.ensure_one()

        line = self.with_company(self.company_id)
        price = line.product_id.lst_price
        product_taxes = line.product_id.taxes_id._filter_taxes_by_company(line.company_id)
        price_unit = line.product_id._get_tax_included_unit_price_from_price(
            price,
            product_taxes=product_taxes,
            fiscal_position=line.repair_id.fiscal_position_id,
        )
        line.update({
            'price_unit': price_unit,
        })

    @api.depends('product_id', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            if not line.product_id:
                line.price_unit = 0.0
            else:
                line._reset_price_unit()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return
        self._reset_price_unit()

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self,
            **{
                'tax_ids': self.tax_id,
                'quantity': self.product_uom_qty,
                'partner_id': self.repair_id.partner_id,
                'currency_id': self.repair_id.currency_id or self.repair_id.company_id.currency_id,
                'rate': self.repair_id.currency_rate,
                **kwargs,
            },
        )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            base_line = line._prepare_base_line_for_taxes_computation()
            self.env['account.tax']._add_tax_details_in_base_line(base_line, line.company_id)
            line.price_subtotal = base_line['tax_details']['raw_total_excluded_currency']
            line.price_total = base_line['tax_details']['raw_total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal

    @api.depends('repair_product_line_type')
    def _compute_forecast_information(self):
        moves_to_compute = self.filtered(lambda move: move.repair_product_line_type == 'part')
        for move in (self - moves_to_compute):
            move.forecast_availability = move.product_qty
            move.forecast_expected_date = False
        return super(StockMove, moves_to_compute)._compute_forecast_information()

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        lines_by_company = defaultdict(lambda: self.env['stock.move'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = None
                if line.product_id:
                    taxes = line.product_id.taxes_id._filter_taxes_by_company(company)
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.repair_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                cache_key += line._get_custom_compute_tax_cache_key()
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

    def _get_custom_compute_tax_cache_key(self):
        """Hook method to be able to set/get cached taxes while computing them"""
        return tuple()

    def _create_repair_sale_order_line(self):
        if not self:
            return
        so_line_vals = []
        for move in self:
            if move.sale_line_id or not move.repair_id.sale_order_id:
                continue
            product_qty = move.product_uom_qty if move.repair_id.state_id.sequence != 5 else move.quantity
            so_line_vals.append({
                'order_id': move.repair_id.sale_order_id.id,
                'product_id': move.product_id.id,
                'product_uom_qty': product_qty, # When relying only on so_line compute method, the sol quantity is only updated on next sol creation
                'product_uom': move.product_uom.id,
                'move_ids': [Command.link(move.id)],
                'qty_delivered': move.quantity if move.repair_id.state_id.sequence == 5 else 0.0,
                'tax_id': [(6, 0, move.tax_id.ids)],
                'discount': move.discount,
                'price_unit': move.price_unit
            })
            if move.repair_id.under_warranty:
                so_line_vals[-1]['price_unit'] = 0.0
            elif move.price_unit:
                so_line_vals[-1]['price_unit'] = move.price_unit

        self.env['sale.order.line'].create(so_line_vals)
