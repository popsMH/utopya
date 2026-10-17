from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import (
    formatLang,
)
import datetime

class ProductCategory(models.Model):
    _inherit = 'product.category'

    active = fields.Boolean(default=False, string='Active')
    name = fields.Char(translate=True)
    product_type = fields.Selection(
        selection=[
            ('consu', 'Goods (Storable)'),
            ('service', 'Service'),
        ],
        string='Product Type',
        required=True,
        default='consu',
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.onchange('categ_id')
    def _onchange_categ_id_force_type(self):
        for rec in self:
            if rec.categ_id and rec.categ_id.product_type:
                rec.type = rec.categ_id.product_type

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'type' in fields_list and res.get('categ_id'):
            categ_id = res.get('categ_id')
            category = self.env['product.category'].browse(
                categ_id if isinstance(categ_id, int) else categ_id[0] if categ_id else False
            )
            if category and category.product_type:
                res['type'] = category.product_type
        return res

    @api.constrains('categ_id', 'type')
    def _check_type_match_category(self):
        for rec in self:
            if rec.categ_id and rec.categ_id.product_type and rec.type != rec.categ_id.product_type:
                raise ValidationError(_(
                    'The product type must be %(type)s for products of the category %(category)s.',
                    type=dict(self.fields_get(['type'])['type']['selection']).get(rec.categ_id.product_type),
                    category=rec.categ_id.display_name,
                ))