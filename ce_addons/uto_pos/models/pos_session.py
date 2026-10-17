from odoo import fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    def get_qualirepar_daily_total(self):
        """Return the total of QualiRépar bonuses granted today.
        Returns a dict {configured, total} for the register closing popup.
        """
        self.ensure_one()
        journal_model = self.env["account.journal"]
        # Guard: the uto_repair module may not be installed
        if "is_repair_bonus" not in journal_model._fields:
            return {"configured": False, "total": 0.0}
        bonus_journal = journal_model.search(
            [
                ("company_id", "=", self.company_id.id),
                ("is_repair_bonus", "=", True),
            ],
            limit=1,
        )
        if not bonus_journal:
            return {"configured": False, "total": 0.0}
        today = fields.Date.today()
        payments = self.env["account.payment"].search(
            [
                ("journal_id", "=", bonus_journal.id),
                ("state", "=", "posted"),
                ("date", "=", today),
            ]
        )
        return {"configured": True, "total": sum(payments.mapped("amount"))}
