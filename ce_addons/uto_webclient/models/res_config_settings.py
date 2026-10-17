# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
import logging

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    odoo_enterprise_url = fields.Char(
        string="Odoo Enterprise URL",
        config_parameter='enterprise_config.odoo_enterprise_url',
        readonly=False,
        help="URL of the Enterprise Odoo Instance",
    )

    @api.model
    def test_connection(self):
        api_url = "/api/test_connection"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("enterprise_config.odoo_enterprise_url")
        if not main_url:
            return _("No URL specified")
        complete_url = main_url + api_url
        try:
            res = requests.post(complete_url, json={}, timeout=30)
        except requests.exceptions.InvalidURL:
            return _("Invalid URL")
        if res.status_code == 200:
            return _("Succesful Connection")
        else:
            return _("Failed Connection")

    @api.model
    def get_subscription_url(self, company_id):
        api_url = "/api/get_subscription"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("enterprise_config.odoo_enterprise_url")
        if not main_url:
            raise ValidationError(_("No odoo enterprise URL found in the settings"))
        complete_url = main_url + api_url
        payload = {
            'related_community_company_id': company_id,
        }
        res = requests.get(complete_url, json=payload, timeout=30)
        if res.status_code == 200:
            result = res.json()
            subscription_portal_url = main_url + "/my/subscriptions/" + str(result['result']['id'])
            return subscription_portal_url
            # return res.json()
        else:
            raise Exception(_("Enterprise API error: %s") % res.text)

    @api.model
    def check_subscription_is_paid(self, company_id):
        api_url = "/api/get_subscription"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("enterprise_config.odoo_enterprise_url")
        if not main_url:
            raise ValidationError(_("No odoo enterprise URL found in the settings"))
        complete_url = main_url + api_url
        payload = {
            'related_community_company_id': company_id,
        }
        res = requests.get(complete_url, json=payload, timeout=30)
        if res.status_code == 200:
            result = res.json()
            is_paid = True if str(result['result']['is_paid']).lower() == 'true' else False
            return is_paid
            # return res.json()
        else:
            raise Exception(_("Enterprise API error: %s") % res.text)
