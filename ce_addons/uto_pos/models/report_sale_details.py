from odoo import api, models

# Correspondance type de moyen de paiement → libellé métier français
_PM_LABELS = {
    'cash': 'Espèces',
    'bank': 'Carte Bancaire (CB)',
    'pay_later': 'Compte Client',
}


class ReportSaleDetails(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_saledetails'

    @api.model
    def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False, **kwargs):
        result = super().get_sale_details(
            date_start=date_start, date_stop=date_stop,
            config_ids=config_ids, session_ids=session_ids, **kwargs
        )

        # Action 1 : Supprimer l'identifiant technique de session (Session ID: POS/XXXXX)
        result['session_name'] = False

        # Action 2 : Supprimer l'affichage de l'unité de mesure
        # Le template n'affiche l'UOM que si line["uom"] != "Units" — on force "Units" comme sentinelle
        for category in result.get('products', []) + result.get('refund_products', []):
            for line in category.get('products', []):
                line['uom'] = 'Units'

        # Action 3 : Nettoyer les noms de moyens de paiement (supprimer " POS/XXXXX")
        pm_ids = [p['id'] for p in result.get('payments', []) if p.get('id')]
        pm_types = (
            {pm.id: pm.type for pm in self.env['pos.payment.method'].browse(pm_ids)}
            if pm_ids else {}
        )
        for payment in result.get('payments', []):
            pm_id = payment.get('id')
            if payment.get('cash'):
                payment['name'] = _PM_LABELS['cash']
            elif pm_id:
                pm_type = pm_types.get(pm_id, '')
                payment['name'] = _PM_LABELS.get(pm_type) or payment['name'].split(' POS/')[0]
            else:
                # Entrée synthétique sans id (espèces sans transaction) : supprimer le suffixe session
                name = payment['name'].split(' POS/')[0]
                payment['name'] = _PM_LABELS['cash'] if name == 'Cash' else name

        return result
