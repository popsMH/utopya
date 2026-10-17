from odoo import _, api, fields, models
from odoo.http import request
import requests
import logging

import unicodedata
import re

class CatalogCatalog(models.Model):
    _name = 'catalog.catalog'
    _description = 'Catalog'

    name = fields.Char('Product Name', required=True, readonly=True)
    # real_catalog_id = fields.Many2one(
    #     'ecosystem.ecologic.catalog',
    #     string='Product to Repair',
    #     required=True,
    # )
    is_available_for_repair = fields.Boolean('Is available for repair ?', readonly=False)
    
    def unlink(self):
        for catalog in self:
            real_catalogs = self.env['ecosystem.ecologic.catalog'].search([('name', '=', catalog.name)])
            real_catalogs.unlink()
        return super().unlink()

    def _make_it_available_for_repair(self):
        for catalog in self:
            catalog.write({
                'is_available_for_repair': not catalog.is_available_for_repair
            })


class BrandBrand(models.Model):
    """ Brand """
    _name = 'brand.brand'
    _description = 'Brand of device'

    name = fields.Char('Brand Name', required=True, readonly=True)
    brand_type = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='Type',
        readonly=True,
        copy=False,
    )
    is_available_for_repair = fields.Boolean('Is available for repair ?', readonly=False)

    def unlink(self):
        for brand in self:
            real_brands = self.env['repair.brand'].search([('name', '=', brand.name)])
            real_brands.unlink()
        return super().unlink()

    def _make_it_available_for_repair(self):
        for brand in self:
            brand.write({
                'is_available_for_repair': not brand.is_available_for_repair
            })


class CodeCode(models.Model):
    """ Code """
    _name = 'code.code'
    _description = 'Repaire Code'

    name = fields.Char('Description', required=True, readonly=True)
    code_type = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='Type',
        readonly=True,
        copy=False,
    )

    def unlink(self):
        for code in self:
            real_codes = self.env['repair.brand'].search([('name', '=', code.name)])
            real_codes.unlink()
        return super().unlink()