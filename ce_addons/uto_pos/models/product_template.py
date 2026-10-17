from odoo import api, models

# Correspondance nom catégorie produit ↔ nom catégorie POS
_CATEG_TO_POS = {
    'Devices': 'Devices',
    'Accessoires': 'Accessoires',
    'Pièces Détachées': 'Pièces Détachées',
    "Main d'œuvre & Forfaits": "Main d'œuvre & Forfaits",
}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_pos_category_for_name(self, categ_name):
        """Retourne le pos.category correspondant au nom de catégorie produit (en anglais)."""
        pos_name = _CATEG_TO_POS.get(categ_name)
        if not pos_name:
            return self.env['pos.category']
        return self.env['pos.category'].with_context(lang='en_US').search([('name', '=', pos_name)], limit=1)

    @api.onchange('categ_id')
    def _onchange_categ_id_sync_pos(self):
        for rec in self:
            if not rec.categ_id:
                rec.pos_categ_ids = [(5,)]
                continue
            categ_name = rec.categ_id.with_context(lang='en_US').name
            pos_categ = rec._get_pos_category_for_name(categ_name)
            rec.pos_categ_ids = [(6, 0, pos_categ.ids)] if pos_categ else [(5,)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'categ_id' in vals and vals['categ_id']:
                categ = self.env['product.category'].browse(vals['categ_id']).with_context(lang='en_US')
                pos_categ = self._get_pos_category_for_name(categ.name)
                if pos_categ:
                    vals['pos_categ_ids'] = [(6, 0, pos_categ.ids)]
        return super().create(vals_list)

    def write(self, vals):
        if 'categ_id' in vals and vals['categ_id']:
            categ = self.env['product.category'].browse(vals['categ_id']).with_context(lang='en_US')
            pos_categ = self._get_pos_category_for_name(categ.name)
            vals = dict(vals, pos_categ_ids=[(6, 0, pos_categ.ids)] if pos_categ else [(5,)])
        return super().write(vals)
