# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Ecologic API fields
    ecologic_api_url = fields.Char(
        string="Ecologic API URL",
        config_parameter='eco_api_config.ecologic_api_url',
        readonly=False,
        help="URL of Ecologic API",
    )

    # Ecosystem API fields
    ecosystem_api_url = fields.Char(
        string="Ecosystem API URL",
        config_parameter='eco_api_config.ecosystem_api_url',
        readonly=False,
        help="URL of Ecosystem API",
    )