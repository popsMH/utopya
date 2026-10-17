from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_cancel(self):
        res = super()._action_cancel()
        posted_inv = self.invoice_ids.filtered(lambda inv: inv.state == 'posted')
        posted_inv.button_draft()
        posted_inv.button_cancel()
        posted_inv.unlink()
        return res

    is_linked_to_repair_order_phone = fields.Boolean("Is linked to repair order phone ?", compute="_check_repair_order_ids")
    ro_name = fields.Char("RO name", compute="_check_repair_order_ids")
    ro_product_to_repair_brand = fields.Char("RO product to repair brand", compute="_check_repair_order_ids")
    ro_product_to_repair_device = fields.Char("RO product to repair device", compute="_check_repair_order_ids")
    ro_product_to_repair_device_id = fields.Char("RO product to repair device id", compute="_check_repair_order_ids")

    @api.depends('repair_order_ids')
    def _check_repair_order_ids(self):
        for order in self:
            order.is_linked_to_repair_order_phone = False
            order.ro_name = " "
            order.ro_product_to_repair_brand = " "
            order.ro_product_to_repair_device = " "
            order.ro_product_to_repair_device_id = " "
            if order.repair_order_ids:
                if order.repair_order_ids[0].is_phone:
                    order.is_linked_to_repair_order_phone = True
                    order.ro_name = order.repair_order_ids[0].name
                    order.ro_product_to_repair_brand = order.repair_order_ids[0].brand_brand_id.name
                    order.ro_product_to_repair_device = order.repair_order_ids[0].commercial_reference
                    order.ro_product_to_repair_device_id = order.repair_order_ids[0].device_id

    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('sale', "Validated"),
            ('cancel', "Cancelled"),
        ]
    )

    def action_print_order(self):
        self.ensure_one()
        return self.env.ref('sale.action_report_saleorder').report_action(self)
