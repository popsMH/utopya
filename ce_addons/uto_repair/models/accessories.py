from odoo import api, Command, fields, models, _

class AccessoriesProvided(models.Model):
    """ Accessories Provided """
    _name = 'accessories.provided'
    _description = 'Accessories Provided'

    name = fields.Char('name', required=True)