from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home

class CustomLogin(Home):
    @http.route()
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        if request.session.uid:  # Check if the user is logged in
            # user first connection
            user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
            if user.is_first_connection:
                redirect_to_url = '/odoo/dashboards'
            else:
                redirect_to_url = '/odoo/companies/{}'.format(user.company_id.id)
            return request.redirect(redirect_to_url)
        return response