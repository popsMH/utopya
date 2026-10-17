# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_offer_type = fields.Selection(
        string="Product Offer Type",
        selection=[
            ('is_standard', "Standard"),
            ('is_premium', "Premium"),
        ],
        required=False,
        default='is_standard',
    )