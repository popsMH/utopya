# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    is_first_connection = fields.Boolean('Is First Connection to the base ?', default=False, store=True)