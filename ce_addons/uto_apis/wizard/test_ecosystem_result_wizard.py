# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TestEcosystemResultWizard(models.TransientModel):
    _name = 'test.ecosystem.result.wizard'
    _description = 'Test Ecosystem Result'

    status = fields.Selection(
        [('success', 'Success'), ('error', 'Error')],
        string='Status',
        readonly=True
    )
    
    message = fields.Text(
        string='Message',
        readonly=True
    )

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}
