# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from markupsafe import Markup


class ResCompany(models.Model):
    _inherit = "res.company"

    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        current_user = self.env.user
        current_user.write({'is_first_connection': True})
        # if current_user.has_group('base.group_system') or current_user.has_group('base.group_erp_manager'):
        #     return res
        # if not current_user.is_first_connection:
        #     for company in self:
        #         if not company.street:
        #             raise ValidationError("Company Address is missing !")
        #         if not company.zip:
        #             raise ValidationError("Company ZIP number is missing !")
        #         if not company.vat:
        #             raise ValidationError("Company VAT number is missing !")
        #         if not company.phone:
        #             raise ValidationError("Company Phone number is missing !")
        #         if not company.country_id:
        #             raise ValidationError("Company Country is missing !")
        #         if not company.siret:
        #             raise ValidationError("Company SIRET is missing !")
        #     current_user.write({'is_first_connection': True})
        return res


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    @api.model
    def _default_company_details(self):
        """The SIRET number appears in the header of the document."""
        company_details = super()._default_company_details()
        company = self.env.company
        if company.siret:
            return company_details + Markup('<br/> %s') % _('SIRET: %s', company.siret)
        return company_details

    company_details = fields.Html(default=_default_company_details)