# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import fields, models, _


class ApiResponse(models.TransientModel):
    _name = 'api.response'
    _description = 'API Response'

    result_message = fields.Text(name="API Result")

