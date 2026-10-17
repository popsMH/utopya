# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    repair_order_ids = fields.One2many(
        comodel_name='repair.order', inverse_name='partner_id',
        string='Repair Order')
    repair_count = fields.Integer(
        "Repair Order(s)", compute='_compute_repair_count')

    vat = fields.Char(index=True, help=False)

    @api.depends('repair_order_ids')
    def _compute_repair_count(self):
        for partner in self:
            partner.repair_count = len(partner.repair_order_ids)

    def action_show_repair(self):
        self.ensure_one()
        if self.repair_count == 1:
            return {
                "type": "ir.actions.act_window",
                "res_model": "repair.order",
                "views": [[False, "form"]],
                "res_id": self.repair_order_ids.id,
            }
        elif self.repair_count > 1:
            return {
                "name": _("Repair Orders"),
                "type": "ir.actions.act_window",
                "res_model": "repair.order",
                "view_mode": "list,form",
                "domain": [('partner_id', '=', self.id)],
            }