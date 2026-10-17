from odoo import _lt, api, models

# Mapping payment method type → business label
_PM_LABELS = {
    'cash': _lt('Cash'),
    'bank': _lt('Credit Card (CB)'),
    'pay_later': _lt('Customer Account'),
}


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False, **kwargs):
        result = super().get_sale_details(
            date_start=date_start, date_stop=date_stop,
            config_ids=config_ids, session_ids=session_ids, **kwargs
        )

        # Action 1: Remove the technical session identifier (Session ID: POS/XXXXX)
        result['session_name'] = False

        # Action 2: Remove the unit of measure display
        # The template only displays the UoM if line["uom"] != "Units" — force "Units" as a sentinel
        for category in result.get('products', []) + result.get('refund_products', []):
            for line in category.get('products', []):
                line['uom'] = 'Units'

        # Action 3: Clean up payment method names (remove " POS/XXXXX")
        pm_ids = [p['id'] for p in result.get('payments', []) if p.get('id')]
        pm_types = (
            {pm.id: pm.type for pm in self.env['pos.payment.method'].browse(pm_ids)}
            if pm_ids else {}
        )
        for payment in result.get('payments', []):
            pm_id = payment.get('id')
            if payment.get('cash'):
                payment['name'] = self.env._(_PM_LABELS['cash'])
            elif pm_id:
                pm_type = pm_types.get(pm_id, '')
                payment['name'] = self.env._(_PM_LABELS[pm_type]) if pm_type in _PM_LABELS else payment['name'].split(' POS/')[0]
            else:
                # Synthetic entry without id (cash without transaction): remove the session suffix
                name = payment['name'].split(' POS/')[0]
                payment['name'] = self.env._(_PM_LABELS['cash']) if name == 'Cash' else name

        return result
