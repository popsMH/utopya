# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    # email = fields.Char(required=True)
    phone = fields.Char(required=False)
    street = fields.Char(required=False)
    zip = fields.Char(required=False)
    city = fields.Char(required=False)

    contact_title = fields.Selection(
        [
            ('1', 'Mr.'),
            ('2', 'Mrs.'),
        ],
        string='Title',
    )

    def _default_country(self):
        default_country = self.env['res.country'].sudo().search([('code', '=', 'FR')], limit=1)
        return default_country

    country_id = fields.Many2one('res.country', default=lambda self: self._default_country())

    @api.model_create_multi
    def create(self, vals_list):
        """ 
        Override the create method to ensure that a company_id is set for the created contact
        """
        current_company = self.env.company
        # set company's country
        default_country = self.env['res.country'].sudo().search([('code', '=', 'FR')], limit=1)
        for vals in vals_list:
            vals['company_id'] = current_company.id
            vals['country_id'] = default_country.id
        return super().create(vals_list)