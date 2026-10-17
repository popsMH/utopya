from odoo import http
from odoo.http import request

class ExternalAPI(http.Controller):

    @http.route('/api/test_connection', type='json', auth='public', methods=['POST'])
    def test_connection(self):
        return "successful connection"

    @http.route('/api/get_subscription', type='json', auth='public', methods=['GET'])
    def get_customer_subscription(self):
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        subscription_vals = {
            "related_community_company_id": payload.get("related_community_company_id"),
        }
        subscription_order = request.env['sale.order'].sudo().search([('related_community_company_id', '=', subscription_vals['related_community_company_id'])], limit=1)
        is_paid = False
        if subscription_order.invoice_ids:
            invoice = subscription_order.invoice_ids[0]
            payment_status = invoice.payment_state
            is_paid = True if payment_status == 'paid' else False
        return {
            "subscription": subscription_order.name if subscription_order else "Empty",
            "id": subscription_order.id if subscription_order else 0,
            "is_paid": is_paid
        }