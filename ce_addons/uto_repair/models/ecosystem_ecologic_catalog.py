from odoo import _, api, fields, models
from odoo.http import request
import requests
import logging

import unicodedata
import re

from odoo.exceptions import ValidationError

class EcosystemEcologicCatalog(models.Model):
    _name = 'ecosystem.ecologic.catalog'
    _description = 'Ecosystem Ecologic Catalog'
    # _rec_name = 'product_name'

    product_id = fields.Char('Product ID', required=True, readonly=True)
    name = fields.Char('Product Name', required=True, readonly=True)
    is_serial_tag_required = fields.Boolean('Is Serial Tag Required ?', readonly=True)
    is_piece_uthorized = fields.Boolean('Is Piece Authorized ?', readonly=True)

    # is_available_for_repair = fields.Boolean('Is available for repair ?', readonly=False)

    catalog_type = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='Type',
        readonly=True,
        copy=False,
    )

    @api.depends('name')
    def _compute_display_name(self):
        for catalog in self:
            name = f"{catalog.name} [{catalog.catalog_type}]"
            catalog.display_name = name

    def _fetch_ecosystem_catalog_data(self):
        """ Retrieve Ecosystem Catalogs """
        # first, need to log in in order to get a fresh token
        login_api_endpoint = 'api/login'
        base_url = request.httprequest.host_url
        # base_url = request.httprequest.host_url.replace("http://", "https://")
        login_api_url = base_url + login_api_endpoint
        response = requests.post(login_api_url, json={}, timeout=30)
        if response.status_code == 200:
            result_login = response.json()  # Parse the JSON response
        else:
            raise Exception(_("Login API error: %s") % response.text)
        if 'result' in result_login and result_login['result']['IdToken']:
            token = result_login['result']['IdToken']
        else:
            raise Exception(_("No token gotten: %s") % result_login)
        # call get_catalog route
        get_catalog_endpoint = 'api/get_catalog'
        # base_url = request.httprequest.host_url
        get_catalog_url = base_url + get_catalog_endpoint
        payload_vals = {
            'brands': 'True',
            'repair-codes': 'True',
            'reimbursement-amounts': 'False',
            'product-sheets': 'False',
            'threshold': 'False',
            'ecologic': 'False',
            'token': token
        }
        response = requests.get(get_catalog_url, json=payload_vals, timeout=30)
        if response.status_code == 200:
            result_catalog = response.json()  # Parse the JSON response
        else:
            raise ValidationError(_("Error has occured :\n %s") % response.text)
        if 'result' in result_catalog:
            all_catalogs = result_catalog['result']['results']
            logging.info(all_catalogs)
            for catalog in all_catalogs:
                ecosystem_ecologic_catalog = self.env['ecosystem.ecologic.catalog']
                existing_catalog = ecosystem_ecologic_catalog.search([('product_id', '=', catalog['ProductID'].strip()), ('catalog_type', '=', 'ecosystem')], limit=1)
                if not existing_catalog:
                    new_catalog = ecosystem_ecologic_catalog.create({
                        'product_id': catalog['ProductID'].strip(),
                        'name': catalog['ProductName'],
                        'is_serial_tag_required': catalog['SerialTagRequired'],
                        'is_piece_uthorized': catalog['PiecAuthorized'],
                        'catalog_type': 'ecosystem',
                    })
                actual_catalog = existing_catalog or new_catalog
                if "Brands" in catalog and catalog['Brands']:
                    for brand in catalog['Brands']:
                        repair_brand = self.env['repair.brand']
                        check_exists = repair_brand.search_count([('brand_id', '=', brand['BrandID'].strip()), ('catalog_id', '=', actual_catalog.id), ('brand_type', '=', 'ecosystem')])
                        if check_exists:
                            continue
                        new_brand = repair_brand.create({
                            'brand_id': brand['BrandID'].strip(),
                            'name': brand['BrandName'].strip(),
                            'is_ecosystem_brand': brand['isEcosystemBrand'],
                            'catalog_id': actual_catalog.id,
                            'brand_type': 'ecosystem'
                        })
                if "RepairCode" in catalog and catalog['RepairCode']:
                    for code in catalog['RepairCode']:
                        repair_code = self.env['repair.code']
                        check_exists = repair_code.search_count([('name', '=', code['Description'].strip()), ('catalog_id', '=', actual_catalog.id), ('code_type', '=', 'ecosystem')])
                        if check_exists:
                            continue
                        new_code = repair_code.create({
                            'code': code['Code'].strip(),
                            'name': code['Description'].strip(),
                            'catalog_id': actual_catalog.id,
                            'code_type': 'ecosystem'
                        })
        else:
            logging.error("Something wrong has occured during catalog data fetching : {}".format(response.text))
        logging.info("End of process")

    def _fetch_ecologic_catalog_data(self):
        """ Retrieve Ecologic Catalogs """
        # first, fetch all products
        get_products_endpoint = 'api/get_labeled_products'
        base_url = request.httprequest.host_url
        # base_url = request.httprequest.host_url.replace("http://", "https://")
        get_products_url = base_url + get_products_endpoint
        response = requests.get(get_products_url, json={}, timeout=30)
        if response.status_code == 200:
            result_products = response.json()  # Parse the JSON response
        else:
            raise Exception(_("Get Porducts API error: %s") % response.text)
        if 'result' in result_products:
            products = result_products['result']['ResponseData']
        else:
            raise Exception(_("No products gotten: %s") % result_products)
        logging.info(products)
        for catalog in products:
            ecosystem_ecologic_catalog = self.env['ecosystem.ecologic.catalog']
            existing_catalog = ecosystem_ecologic_catalog.search([('product_id', '=', catalog['ProductId'].strip()), ('catalog_type', '=', 'ecologic')], limit=1)
            if not existing_catalog:
                new_catalog = ecosystem_ecologic_catalog.create({
                    'product_id': catalog['ProductId'].strip(),
                    'name': catalog['ProductName'],
                    'catalog_type': 'ecologic',
                })
            actual_catalog = existing_catalog or new_catalog
            if "RepairCodes" in catalog and catalog['RepairCodes']:
                for code in catalog['RepairCodes']:
                    repair_code = self.env['repair.code']
                    check_exists = repair_code.search_count([('name', '=', code['Label'].strip()), ('catalog_id', '=', actual_catalog.id), ('code_type', '=', 'ecologic')])
                    if check_exists:
                        continue
                    new_code = repair_code.create({
                        'code': code['Code'].strip(),
                        'name': code['Label'].strip(),
                        'catalog_id': actual_catalog.id,
                        'code_type': 'ecologic'
                    })
        # second, fetch all brands
        get_brands_endpoint = 'api/get_brands'
        get_brands_url = base_url + get_brands_endpoint
        response = requests.get(get_brands_url, json={}, timeout=30)
        if response.status_code == 200:
            result_brands = response.json()  # Parse the JSON response
        else:
            raise Exception(_("Get brands API error: %s") % response.text)
        if 'result' in result_brands:
            brands = result_brands['result']['ResponseData']
        else:
            raise Exception(_("No brands gotten: %s") % result_brands)
        logging.info(products)
        for brand in brands:
            repair_brand = self.env['repair.brand']
            existing_brand = repair_brand.search_count([('brand_id', '=', brand['BrandId'].strip()), ('brand_type', '=', 'ecologic')])
            if not existing_brand:
                new_brand = repair_brand.create({
                    'brand_id': brand['BrandId'].strip(),
                    'name': brand['BrandName'].strip(),
                    'is_ecologic_brand': True,
                    'brand_type': 'ecologic'
                })
        logging.info("End of process")

    @api.model_create_multi
    def create(self, vals_list):
        # Rename product names before creating records
        for vals in vals_list:
            if "name" in vals:
                vals["name"] = self._rename_product(vals["name"])
        
        catalog = super(EcosystemEcologicCatalog, self).create(vals_list)
        
        # Create catalog.catalog reference with renamed name
        for catalog_record in catalog:
            if not self.env['catalog.catalog'].search([('name', '=', catalog_record.name.strip())]):
                self.env['catalog.catalog'].create({'name': catalog_record.name.strip()})
        
        return catalog

    def _normalize(self, text):
        """Normalize text by removing accents and converting to lowercase"""
        if not text:
            return ""
        # Remove accents
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode('utf-8')
        # Lowercase, trim, and clean spaces
        text = " ".join(text.lower().strip().split())
        return text

    def _rename_product(self, name):
        """Rename French product names to English equivalents"""
        normalized = self._normalize(name)
        mapping = {
            "telephone portable": "Smartphone",
            "ordinateur portable": "Laptop",
        }
        # Return mapped name if found, otherwise return original
        renamed = mapping.get(normalized, name)
        return renamed