from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from random import randint

# class Device(models.Model):
#     """ Device """
#     _name = 'repair.device'
#     _description = 'Device to repair'

#     name = fields.Char('name', required=True)

class Brand(models.Model):
    """ Brand """
    _name = 'repair.brand'
    _description = 'Brand of device'

    catalog_id = fields.Many2one(
        'ecosystem.ecologic.catalog',
        string='Catalog',
        required=False,
        readonly=True
    )
    name = fields.Char('Brand Name', required=True, readonly=True)
    brand_id = fields.Char('Brand ID', readonly=True)
    is_ecosystem_brand = fields.Boolean('Is Ecosystem Brand ?', readonly=True, default=False)
    is_ecologic_brand = fields.Boolean('Is Ecologic Brand ?', readonly=True, default=False)
    code = fields.Char('Code')
    organization = fields.Char('Organization')
    brand_type = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='Type',
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        brand = super(Brand, self).create(vals_list)
        if not self.env['brand.brand'].search([('name', '=', brand.name.strip()), ('brand_type', '=', brand.brand_type)]):
            self.env['brand.brand'].create({'name': brand.name.strip(), 'brand_type': brand.brand_type})
        return brand


# class Model(models.Model):
#     """ Model """
#     _name = 'repair.model'
#     _description = 'Model of device'

#     name = fields.Char('name', required=True)

class RepairCode(models.Model):
    """ Repair Code """
    _name = 'repair.code'
    _description = 'Repaire Code'

    name = fields.Char('Description', required=True, readonly=True)
    code = fields.Char('Code', required=True, readonly=True)
    catalog_id = fields.Many2one(
        'ecosystem.ecologic.catalog',
        string='Catalog',
        required=False,
        readonly=True
    )
    code_type = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='Type',
        readonly=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        code = super(RepairCode, self).create(vals_list)
        name = code.name.strip().replace('É', 'E')
        if not self.env['code.code'].search([('name', '=', name)]):
            self.env['code.code'].create({'name': name})
        return code


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.depends_context('show_phone_and_email')
    def _compute_display_name(self):
        if not self.env.context.get('show_phone_and_email'):
            return super()._compute_display_name()
        for partner in self:
            res = ""
            if partner.phone:
                res += f" {partner.phone} \n"
            if partner.email:
                res += f" {partner.email}"
            partner.display_name = f"{partner.name} \n" + res


class RepairState(models.Model):
    _name = "repair.state"
    _description = "Repair States"
    _rec_name = 'name'
    _order = "sequence, id"

    name = fields.Char('State Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order states. Lower is better.")
    is_unclickable = fields.Boolean('Is Unclickable State ?')
    is_cancelled = fields.Boolean('Is Cancelled State ?')
    is_done = fields.Boolean('Is Done State ?')


class RepairStateHelper(models.Model):
    _name = "repair.state.helper"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True, translate=True, readonly=False)
    color = fields.Integer('Color', default=_get_default_color)
    sequence = fields.Integer('Sequence', default=1, help="Used to order states. Lower is better.")


class CommercialReference(models.Model):
    _name = "commercial.reference"
    _description = "Commercial Reference"
    _rec_name = 'name'

    name = fields.Char('Label', required=True, copy=False,)
    brand_brand_id = fields.Many2one(
        'brand.brand',
        string='Brand',
        required=False,
        copy=False,
    )
    
    _sql_constraints = [
        (
            'unique_name_per_brand',
            'unique(name, brand_brand_id)',
            _('The label must be unique per brand.')
        ),
    ]

    @api.constrains('name', 'brand_brand_id')
    def _check_unique_name_when_no_brand(self):
        for record in self:
            if not record.brand_brand_id:
                domain = [
                    ('id', '!=', record.id),
                    ('name', '=', record.name),
                    ('brand_brand_id', '=', False),
                ]
                if self.search_count(domain):
                    raise ValidationError(
                        _('The label must be unique.')
                    )


class DeviceCapacity(models.Model):
    _name = "device.capacity"
    _description = "Device Capacity"
    _rec_name = 'name'
    _order = "sequence, name"

    name = fields.Char('Name', required=True, translate=True)
    default_code = fields.Char('Code', required=True, translate=True)
    value = fields.Char('Value', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    device_type = fields.Selection(
        [
            ('laptop', 'Laptop'),
            ('smartphone', 'Smartphone'),
            ('smartwatch', 'Smartwatch'),
            ('tablet', 'Tablet'),
        ],
        string='Device Type',
        required=True,
    )


class DeviceColor(models.Model):
    _name = "device.color"
    _description = "Device Color"
    _rec_name = 'name'
    _order = "sequence, name"

    name = fields.Char('Name', required=True, translate=True)
    default_code = fields.Char('Code', required=True, translate=True)
    value = fields.Char('Value', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    device_type = fields.Selection(
        [
            ('laptop', 'Laptop'),
            ('smartphone', 'Smartphone'),
            ('smartwatch', 'Smartwatch'),
            ('tablet', 'Tablet'),
        ],
        string='Device Type',
        required=True,
    )