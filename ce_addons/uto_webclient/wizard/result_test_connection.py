# -*- coding: utf-8 -*-

from markupsafe import Markup
from odoo import fields, models, _


class ResultTestConnection(models.TransientModel):
    _name = 'result.test.connection'
    _description = 'result test connection'

    result_message = fields.Char(name="Connection Result")

