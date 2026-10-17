# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import requests

class ResCompany(models.Model):
    _inherit = "res.company"

    is_quali_repar = fields.Boolean(string="QualiRépar", default=False)

    ecologic_api_url = fields.Char(
        string="Ecologic API URL",
        readonly=False
    )

    ecologic_api_key = fields.Char(
        string="Ecologic API Key",
        readonly=False,
    )

    ecosystem_api_url = fields.Char(
        string="Ecosystem API URL",
        readonly=False
    )

    ecosystem_api_username = fields.Char(
        string="Ecosystem API Username",
        readonly=False,
    )

    ecosystem_api_password = fields.Char(
        string="Ecosystem API Password",
        readonly=False,
    )

    def action_test_ecosystem(self):
        login_api_endpoint = 'api/login'
        base_url = request.httprequest.host_url
        # base_url = request.httprequest.host_url.replace("http://", "https://")
        login_api_url = base_url + login_api_endpoint
        response = requests.post(login_api_url, json={}, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data['result']:
                status = 'error'
                message = response_data['result']['error']['message']
            else:
                status = 'success'
                message = _("Test API is working correctly.")
        else:
            status = 'error'
            message = _("Test API error: %s") % response.text
        
        # Create wizard record with the result
        wizard = self.env['test.ecosystem.result.wizard'].create({
            'status': status,
            'message': message,
        })
        
        # Return action to open the wizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'test.ecosystem.result.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_test_ecologic(self):
        get_repair_api_endpoint = 'api/get_repair_site'
        base_url = request.httprequest.host_url
        # base_url = request.httprequest.host_url.replace("http://", "https://")
        get_repair_api_url = base_url + get_repair_api_endpoint
        response = requests.get(get_repair_api_url, json={}, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            if 'error' in response_data:
                status = 'error'
                message = response_data['error']['data']['message']
            else:
                status = 'success'
                message = _("Test API is working correctly.")
        else:
            status = 'error'
            message = _("Test API error: %s") % response.text
        
        # Create wizard record with the result
        wizard = self.env['test.ecosystem.result.wizard'].create({
            'status': status,
            'message': message,
        })
        
        # Return action to open the wizard
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'test.ecosystem.result.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }