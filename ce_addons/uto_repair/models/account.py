from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import (
    formatLang,
)
import datetime

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_repair_bonus = fields.Boolean('Is repair bonus ?')

    @api.constrains('is_repair_bonus')
    def _check_bonus_journal_more_than_one(self):
        for journal in self:
            bonus_journal = self.env['account.journal'].search([('is_repair_bonus', '=', True), ('id', '!=', journal.id), ('company_id', '=', journal.company_id.id)])
            if journal.is_repair_bonus:
                if bonus_journal:
                    raise ValidationError(_("There has to be only one Bonus Journal per Company !"))

class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Validated'),
            ('cancel', 'Cancelled'),
        ],
    )

    is_linked_to_ecosystem_eligible_repair = fields.Boolean("Is linked to a repair eligible for Ecosystem or Ecologic ?", compute="_check_repair_order_eligibility")
    is_linked_to_repair_order_phone = fields.Boolean("Is linked to repair order phone ?", compute="_check_repair_order_eligibility")
    ro_name = fields.Char("RO name", compute="_check_repair_order_eligibility")
    ro_product_to_repair_brand = fields.Char("RO product to repair brand", compute="_check_repair_order_eligibility")
    ro_product_to_repair_device = fields.Char("RO product to repair device", compute="_check_repair_order_eligibility")
    ro_product_to_repair_device_id = fields.Char("RO product to repair device id", compute="_check_repair_order_eligibility")

    @api.depends('line_ids.sale_line_ids')
    def _check_repair_order_eligibility(self):
        for move in self:
            move.is_linked_to_ecosystem_eligible_repair = False
            move.is_linked_to_repair_order_phone = False
            move.ro_name = " "
            move.ro_product_to_repair_brand = " "
            move.ro_product_to_repair_device = " "
            move.ro_product_to_repair_device_id = " "
            # if move.line_ids.sale_line_ids.order_id.repair_order_ids and move.line_ids.sale_line_ids.order_id.repair_order_ids[0].if_eligible:
            if move.line_ids.sale_line_ids.order_id.repair_order_ids:
                if move.line_ids.sale_line_ids.order_id.repair_order_ids[0].if_eligible:
                    move.is_linked_to_ecosystem_eligible_repair = True
                if move.line_ids.sale_line_ids.order_id.repair_order_ids[0].is_phone:
                    move.is_linked_to_repair_order_phone = True
                    move.ro_name = move.line_ids.sale_line_ids.order_id.repair_order_ids[0].name
                    move.ro_product_to_repair_brand = move.line_ids.sale_line_ids.order_id.repair_order_ids[0].repair_brand_id.name
                    move.ro_product_to_repair_device = move.line_ids.sale_line_ids.order_id.repair_order_ids[0].commercial_reference
                    move.ro_product_to_repair_device_id = move.line_ids.sale_line_ids.order_id.repair_order_ids[0].device_id

    @api.depends('move_type', 'line_ids.amount_residual')
    def _compute_payments_widget_reconciled_info(self):
        for move in self:
            payments_widget_vals = {'title': _('Less Payment'), 'outstanding': False, 'content': []}

            if move.state == 'posted' and move.is_invoice(include_receipts=True):
                reconciled_vals = []
                reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
                for reconciled_partial in reconciled_partials:
                    counterpart_line = reconciled_partial['aml']
                    if counterpart_line.move_id.ref:
                        reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
                    else:
                        reconciliation_ref = counterpart_line.move_id.name
                    if counterpart_line.amount_currency and counterpart_line.currency_id != counterpart_line.company_id.currency_id:
                        foreign_currency = counterpart_line.currency_id
                    else:
                        foreign_currency = False

                    reconciled_vals.append({
                        'name': counterpart_line.name,
                        'journal_name': counterpart_line.journal_id.name,
                        'is_journal_repair_bonus': counterpart_line.journal_id.is_repair_bonus,
                        'company_name': counterpart_line.journal_id.company_id.name if counterpart_line.journal_id.company_id != move.company_id else False,
                        'amount': reconciled_partial['amount'],
                        'currency_id': move.company_id.currency_id.id if reconciled_partial['is_exchange'] else reconciled_partial['currency'].id,
                        'date': counterpart_line.date,
                        'partial_id': reconciled_partial['partial_id'],
                        'account_payment_id': counterpart_line.payment_id.id,
                        'payment_method_name': counterpart_line.payment_id.payment_method_line_id.name,
                        'move_id': counterpart_line.move_id.id,
                        'is_refund': counterpart_line.move_id.move_type in ['in_refund', 'out_refund'],
                        'ref': reconciliation_ref,
                        # these are necessary for the views to change depending on the values
                        'is_exchange': reconciled_partial['is_exchange'],
                        'amount_company_currency': formatLang(self.env, abs(counterpart_line.balance), currency_obj=counterpart_line.company_id.currency_id),
                        'amount_foreign_currency': foreign_currency and formatLang(self.env, abs(counterpart_line.amount_currency), currency_obj=foreign_currency)
                    })
                payments_widget_vals['content'] = reconciled_vals

            if payments_widget_vals['content']:
                move.invoice_payments_widget = payments_widget_vals
            else:
                move.invoice_payments_widget = False

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.move_type == 'out_invoice' and move.is_linked_to_ecosystem_eligible_repair:   # customer invoice only
                partial_amount = float()
                if move.amount_total > 25:
                    partial_amount = 25
                    move._create_automatic_partial_payment(partial_amount)
        return res

    def _create_automatic_partial_payment(self, partial_amount):
        """Create the first part of the payment automatically."""
        self.ensure_one()
        # amount to pay
        # partial_amount = 25  
        # Pick bonus journal
        bonus_account_journal = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('is_repair_bonus', '=', True)])
        if not bonus_account_journal:
            return
        payment_vals = {
            'payment_type': 'inbound',
            'partner_id': self.partner_id.id,
            'amount': partial_amount,
            'currency_id': self.currency_id.id,
            'journal_id': bonus_account_journal.id,
            'memo': f"{self.name} - Repair Bonus",
            'date': datetime.datetime.now().date(),
        }
        payment = self.env['account.payment'].create(payment_vals)
        # Post payment
        payment.action_post()
        # Reconcile automatically
        (payment.move_id.line_ids + self.line_ids).filtered(
            lambda l: l.account_id == self.partner_id.property_account_receivable_id
        ).reconcile()
        # link the payment to the invoice to see them in both forms (invoice and payment)
        payment.write({'invoice_ids': [(4, self.id)]})