# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    odoo_community_url = fields.Char(
        string="Odoo Community URL",
        config_parameter='community_config.odoo_community_url',
        readonly=False,
        help="URL of the Community Odoo Instance",
    )
