# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_occasion = fields.Boolean(string="Second-hand Product", default=False)

    @api.onchange('is_occasion')
    def _onchange_is_occasion(self):
        if not self.env.company.is_margin_vat:
            return
        margin_tax = self.env.ref('uto_base.account_tax_tva_marge_20', raise_if_not_found=False)
        if not margin_tax:
            return
        if self.is_occasion:
            self.taxes_id = [(4, margin_tax.id)]
        else:
            self.taxes_id = [(3, margin_tax.id)]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_occasion_tax()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'is_occasion' in vals:
            self._sync_occasion_tax()
        return result

    def _sync_occasion_tax(self):
        if not self.env.company.is_margin_vat:
            return
        margin_tax = self.env.ref('uto_base.account_tax_tva_marge_20', raise_if_not_found=False)
        if not margin_tax:
            return
        for product in self:
            if product.is_occasion:
                if margin_tax not in product.taxes_id:
                    product.taxes_id = [(4, margin_tax.id)]
            else:
                if margin_tax in product.taxes_id:
                    product.taxes_id = [(3, margin_tax.id)]
