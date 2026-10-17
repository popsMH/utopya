# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

class SaleOrder(models.Model):
    _inherit = "sale.order"

    subscription_offer_type = fields.Selection(
        string="Subscription Offer Type",
        selection=[
            ('is_standard', "Standard"),
            ('is_premium', "Premium"),
        ],
        compute='_compute_subscription_offer_type',
    )

    related_community_company_id = fields.Integer("Company ID", store=True)
    related_community_user_id = fields.Integer("User ID", store=True)

    @api.depends('order_line')
    def _compute_subscription_offer_type(self):
        for order in self:
            if order.order_line:
                if all(line.product_template_id.product_offer_type == 'is_standard' for line in order.order_line):
                    order.subscription_offer_type = 'is_standard'
                elif all(line.product_template_id.product_offer_type == 'is_premium' for line in order.order_line):
                    order.subscription_offer_type = 'is_premium'
                else:
                    order.subscription_offer_type = False
            else:
                order.subscription_offer_type = False

    @api.model
    def test_connection(self):
        api_url = "/api/test_connection"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("community_config.odoo_community_url")
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

    # create company in community instance
    def _collect_partner_data(self, partner):
        fields_to_send = [
            "name", "street", "street2", "zip", "city",
            "phone", "mobile", "email", "vat", "website"
        ]
        data = {}
        for field in fields_to_send:
            value = getattr(partner, field, None)
            if value:
                data[field] = value
        if partner.country_id:
            data["country_id"] = partner.country_id.id
        return data

    @api.model
    def _provision_in_community(self, vals):
        # community_url = "http://localhost:8028/api/create_company"
        api_url = "/api/create_company"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("community_config.odoo_community_url")
        if not main_url:
            raise ValidationError(_("No odoo community URL found in the settings"))
        complete_url = main_url + api_url
        payload = {
            'company_name': vals.get("company_name"),
            'email': vals.get("email"),
            'plan': vals.get("plan"),
            'street': vals.get("street"),
            'street2': vals.get("street2"),
            'zip': vals.get("zip"),
            'city': vals.get("city"),
            'phone': vals.get("phone"),
            'vat': vals.get("vat"),
            'website': vals.get("website"),
            'country_id': vals.get("country_id"),
        }
        res = requests.post(complete_url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Community API error: %s") % res.text)

    @api.model
    def _create_company_pos_in_community(self, vals):
        # community_url = "http://localhost:8028/api/create_company"
        api_url = "/api/set_company_pos"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("community_config.odoo_community_url")
        if not main_url:
            raise ValidationError(_("No odoo community URL found in the settings"))
        complete_url = main_url + api_url
        payload = {
            'company_id': vals.get("company_id")
        }
        res = requests.post(complete_url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Community API error: %s") % res.text)

    def action_confirm(self):
        res = super().action_confirm()
        for sub in self:
            partner = sub.partner_id
            data = self._collect_partner_data(partner)
            # info linked to the subscription
            data.update({
                "company_name": partner.name,
                "plan": sub.subscription_offer_type,
            })
            # data = {
            #     "company_name": sub.partner_id.name,
            #     "email": sub.partner_id.email or "user_admin",
            #     "plan": sub.subscription_offer_type,
            # }
            response = self._provision_in_community(data)
            if 'error' in response:
                raise ValidationError(_('Something is wrong with company creation, please reach out the admin. error : %s') % response)
            body = _("Community company created: %s") % response['result']
            sub.message_post(body=body)
            # stock company_id and user_id in the subscription form in bid to get them easily next time we use it
            sub.write({
                'related_community_company_id': response['result']['Company_ID'],
                'related_community_user_id': response['result']['User_ID']
            })
            # create POS related to the company
            pos_response = self._create_company_pos_in_community({'company_id': response['result']['Company_ID']})
            if 'error' in pos_response:
                logging.error('Oups, POS not created : {}'.format(pos_response))
            else:
                logging.info('Nice, POS created : {}'.format(pos_response['result']))
        return res

    # archive company in community instance
    @api.model
    def _archive_company_in_community(self, vals):
        # community_url = "http://localhost:8028/api/archive_company"
        api_url = "/api/archive_company"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("community_config.odoo_community_url")
        if not main_url:
            raise ValidationError(_("No odoo community URL found in the settings"))
        complete_url = main_url + api_url
        payload = {
            'company_id': vals.get("company_id"),
            'user_id': vals.get("user_id"),
        }
        res = requests.post(complete_url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Community API error: %s") % res.text)

    def set_close(self, close_reason_id=None, renew=False):
        res = super().set_close(close_reason_id, renew)
        for sub in self:
            data = {
                "company_id": sub.related_community_company_id,
                "user_id": sub.related_community_user_id,
            }
            response = self._archive_company_in_community(data)
            body = _("Community company archived: %s") % response['result']
            sub.message_post(body=body)
        return res

    # unarchive company in community instance
    @api.model
    def _unarchive_company_in_community(self, vals):
        # community_url = "http://localhost:8028/api/unarchive_company"
        api_url = "/api/unarchive_company"
        params = self.env["ir.config_parameter"].sudo()
        main_url = params.get_param("community_config.odoo_community_url")
        if not main_url:
            raise ValidationError(_("No odoo community URL found in the settings"))
        complete_url = main_url + api_url
        payload = {
            'company_id': vals.get("company_id"),
            'user_id': vals.get("user_id"),
        }
        res = requests.post(complete_url, json=payload, timeout=30)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(_("Community API error: %s") % res.text)

    def set_open(self):
        res = super().set_open()
        for sub in self:
            data = {
                "company_id": sub.related_community_company_id,
                "user_id": sub.related_community_user_id,
            }
            response = self._unarchive_company_in_community(data)
            body = _("Community company unarchived: %s") % response['result']
            sub.message_post(body=body)
        return res