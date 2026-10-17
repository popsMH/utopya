from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import (
    formatLang,
)
import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    list_price = fields.Float(
        string='Price incl. tax',
        help=False
    )

    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id',
        string="VAT",
        help=False
    )

    standard_price = fields.Float(compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits='Product Price', groups="base.group_user",
        help=False)

    type = fields.Selection(
        help=False
    )

    invoice_policy = fields.Selection(
        compute='_compute_invoice_policy',
        help=False)

    # supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id',
    #     help=False
    # )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['invoice_policy'] = 'order'
            vals['available_in_pos'] = True       
            vals['sale_ok'] = True
        return super().create(vals_list)

    def write(self, vals):
        if 'invoice_policy' in vals or ('type' in vals and vals['type'] in ['consu', 'service']):
            vals['invoice_policy'] = 'order'
        return super().write(vals)

    