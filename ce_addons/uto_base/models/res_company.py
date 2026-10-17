# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    is_margin_vat = fields.Boolean(string="Enable VAT on Margin (Second-hand Sales)", default=False)
    margin_vat_legal_mention = fields.Char(
        string="Legal Mention on Second-hand Invoices",
        default="TVA sur marge - Article 297 A du CGI",
    )

    def write(self, vals):
        result = super().write(vals)
        if 'is_margin_vat' in vals:
            self._sync_all_occasion_products()
        return result

    def _sync_all_occasion_products(self):
        margin_tax = self.env.ref('uto_base.account_tax_tva_marge_20', raise_if_not_found=False)
        if not margin_tax:
            return
        occasion_products = self.env['product.template'].search([
            ('is_occasion', '=', True),
            ('company_id', 'in', self.ids + [False]),
        ])
        for company in self:
            company_products = occasion_products.filtered(
                lambda p: not p.company_id or p.company_id == company
            )
            if company.is_margin_vat:
                company_products.filtered(
                    lambda p: margin_tax not in p.taxes_id
                ).write({'taxes_id': [(4, margin_tax.id)]})
            else:
                company_products.filtered(
                    lambda p: margin_tax in p.taxes_id
                ).write({'taxes_id': [(3, margin_tax.id)]})
