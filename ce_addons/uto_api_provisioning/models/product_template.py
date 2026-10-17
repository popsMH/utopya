# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        """ 
        Override the create method to ensure that a company_id is set for the created product template
        """
        current_company = self.env.company
        for vals in vals_list:
            vals['company_id'] = current_company.id
        return super().create(vals_list)

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals_list):
        """ 
        Override the create method to ensure that a company_id is set for the created product product
        """
        current_company = self.env.company
        for vals in vals_list:
            vals['company_id'] = current_company.id
        return super().create(vals_list)