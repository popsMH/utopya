from odoo import http
from odoo.http import request

class ProvisioningAPI(http.Controller):

    @http.route('/api/test_connection', type='json', auth='public', methods=['POST'])
    def test_connection(self):
        return "successful connection"
            
    @http.route('/api/create_company', type='json', auth='public', methods=['POST'])
    def create_company(self):
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        company_currency = request.env['res.currency'].sudo().search([('name', '=', 'EUR')])
        company_vals = {
            "name": payload.get("company_name"),
            "street": payload.get("street"),
            "street2": payload.get("street2"),
            "zip": payload.get("zip"),
            "city": payload.get("city"),
            "phone": payload.get("phone"),
            "email": payload.get("email"),
            "vat": payload.get("vat"),
            "website": payload.get("website"),
            # "country_id": payload.get("country_id"),
        }
        if company_currency:
            company_vals.update({
                "currency_id": company_currency.id,
            })
        company = request.env['res.company'].sudo().create(company_vals)
        # set company of its partner_id 
        company_partner_id = company.partner_id
        company_partner_id.sudo().write({'company_id': company.id})
        user = request.env['res.users'].sudo().create({
            'name': payload.get('company_name') + " Admin",
            'login': payload.get('email'),
            'company_id': company.id,                # default company
            'company_ids': [(6, 0, [company.id])],   # reset allowed companies to only this one
            'groups_id': [(6, 0, self._map_groups(payload.get('plan')))],
            'lang': 'fr_FR' # set french as default language
        })
        # set contact mail
        partner = user.partner_id
        partner.sudo().write({'email': user.login})
        self._create_default_data(company)
        # user.action_reset_password()
        return {
            "Company_ID": company.id,
            "Company": company.name,
            "User_ID": user.id,
            "User": user.name,
            "Login": user.login,
        }

    def _map_groups(self, plan):
        """Assign groups according to Standard/Premium plan"""
        groups = []
        groups.append(request.env.ref("base.group_user").id)
        # groups.append(request.env.ref("base.group_erp_manager").id)
        groups.extend([
            request.env.ref("point_of_sale.group_pos_user").id,
            request.env.ref("stock.group_stock_user").id,
            request.env.ref("account.group_account_invoice").id,
            request.env.ref("uto_api_provisioning.group_company_main_user").id,
            request.env.ref("sales_team.group_sale_manager").id,
            # + API access, etc.
        ])
        # if plan == "Standard":
        #     groups.append(request.env.ref("point_of_sale.group_pos_user").id)
        # if plan == "Premium":
        #     groups.extend([
        #         request.env.ref("point_of_sale.group_pos_manager").id,
        #         # + API access, repair, etc.
        #     ])
        return groups

    def _create_default_data(self, company):
        """ Create minimal data for a company """
        ## warehouse
        warehouse_data = {
            'name': company.name,
            'code': 'WH',
            'company_id': company.id,
            'partner_id': company.partner_id.id     
        }
        warehouse = request.env['stock.warehouse'].sudo().create(warehouse_data)
        # set company's country
        default_country = request.env['res.country'].sudo().search([('code', '=', 'FR')], limit=1)
        company.write({'country_id': default_country.id})
        # set company report layout as bubble
        bubble_report_layout_id = request.env['report.layout'].sudo().search([('view_id.name', '=', 'external_layout_bubble')])
        company.write({'external_report_layout_id': bubble_report_layout_id.view_id.id})

    @http.route('/api/set_company_pos', type='json', auth='public', methods=['POST'])
    def set_company_pos(self):
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        company = request.env['res.company'].sudo().search([('id', '=', payload.get('company_id'))])
        # # # # point of sale
        pos_data = {
            'name': 'Caisse Principale'
        }
        point_of_sale = request.env['pos.config'].sudo().with_company(company).create(pos_data)
        # enable the category bar with the 4 predefined business categories
        pos_categories = request.env['pos.category'].sudo().search([
            ('name', 'in', ['Devices', 'Accessoires', 'Pièces Détachées', "Main d'œuvre & Forfaits"]),
        ])
        if pos_categories:
            point_of_sale.sudo().write({
                'limit_categories': True,
                'iface_available_categ_ids': [(6, 0, pos_categories.ids)],
            })
        # create repair bonus journal
        account_account_data = {
            'code': '512004',
            'name': 'Banque Bonus reparation',
            'account_type': 'asset_cash',
            'company_ids': [(6, 0, [company.id])]
        }
        account_account = request.env['account.account'].sudo().with_company(company).create(account_account_data)
        account_journal_data = {
            'name': 'Banque Bonus reparation',
            'type': 'bank',
            'is_repair_bonus': True,
            'company_id': company.id,
            'default_account_id': account_account.id,
            'code': 'BNK2',
            'payment_sequence': True
        }
        account_journal = request.env['account.journal'].sudo().with_company(company).create(account_journal_data)
        # remove customer account payment method that is created natively after POS creation
        cust_acc_domain = [
            ('company_id', '=', company.id),
            ('split_transactions', '=', True),
            ('journal_id', '=', False),
        ]
        customer_account_payment_method = request.env['pos.payment.method'].sudo().with_company(company).search(cust_acc_domain)
        if customer_account_payment_method:
            customer_account_payment_method.sudo().write({'active': False})
            # customer_account_payment_method.sudo().unlink()
        return {
            "POS ID": point_of_sale.id,
            "POS Name": point_of_sale.name
        }

    @http.route('/api/archive_company', type='json', auth='public', methods=['POST'])
    def archive_company(self):
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        company_vals = {
            "company_id": payload.get("company_id"),
            "user_id": payload.get("user_id"),
        }
        user = request.env['res.users'].sudo().search([('id', '=', company_vals['user_id'])])
        user.sudo().action_archive()
        company = request.env['res.company'].search([('id', '=', company_vals['company_id'])])
        company.sudo().toggle_active()  
        return {
            "Company": company.name,
            "User": user.name,
        }

    @http.route('/api/unarchive_company', type='json', auth='public', methods=['POST'])
    def unarchive_company(self):
        data = getattr(request, 'httprequest', None)
        if not data:
            return {"error": "empty_payload", "raw": str(request.httprequest.get_data(as_text=True))}
        payload = data.json
        company_vals = {
            "company_id": payload.get("company_id"),
            "user_id": payload.get("user_id"),
        }
        company = request.env['res.company'].sudo().search([('id', '=', company_vals['company_id']), ('active', '=', False)])
        company.sudo().toggle_active()  
        user = request.env['res.users'].sudo().search([('id', '=', company_vals['user_id']), ('active', '=', False)])
        user.sudo().action_unarchive()
        user.sudo().write({'company_ids': [(6, 0, [company.id])]})
        return {
            "Company": company.name,
            "User": user.name,
        }