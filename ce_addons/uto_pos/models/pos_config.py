from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id')
            if self.env['pos.config'].search_count([('company_id', '=', company_id)]):
                raise ValidationError(_('Cannot have more that one Point of Sale !'))
        return super().create(vals_list)

    def _action_to_open_ui(self):
        action = super()._action_to_open_ui()
        action['target'] = 'new'
        return action

    @api.model
    def action_open_pos_direct(self):
        """If a single register exists for the company, open the POS interface directly.
        Otherwise, fall back to the standard kanban dashboard."""
        config = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if config:
            return config.open_ui()
        return self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_config_kanban')

    @api.model
    def _uto_configure_pos_categories(self):
        """Called once at install: enable the category bar on the POS
        and attach the 4 business categories to it."""
        categories = self.env['pos.category'].search([
            ('name', 'in', ['Devices', 'Accessoires', 'Pièces Détachées', "Main d'œuvre & Forfaits"]),
        ])
        for config in self.search([]):
            config.write({
                'limit_categories': True,
                'iface_available_categ_ids': [(6, 0, categories.ids)],
            })