from odoo import api, Command, fields, models, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
import requests
import logging

import base64
import imghdr

import pytz

import unicodedata
import re

class Repair(models.Model):
    """ Repair Orders """
    _inherit = 'repair.order'

    partner_id = fields.Many2one(
        'res.partner',
        index=True, check_company=True, change_default=True, compute='_compute_partner_id', readonly=False, store=True,
        help=False
    )

    contact_phone = fields.Char('Contact Phone')
    visual_condition = fields.Char('Visual Condition')

    name = fields.Char(string='Reference',)

    # Picking & Locations
    picking_type_id = fields.Many2one(
        'stock.picking.type',
        required=False, 
    )
    location_id = fields.Many2one(
        'stock.location',
        required=False
    )
    product_location_src_id = fields.Many2one(
        'stock.location',
        required=False
    )
    product_location_dest_id = fields.Many2one(
        'stock.location',
        required=False
    )
    location_dest_id = fields.Many2one(
        'stock.location',
        required=False
    )
    parts_location_id = fields.Many2one(
        'stock.location',
        required=False
    )
    recycle_location_id = fields.Many2one(
        'stock.location',
        required=False
    )

    # new fields
    catalog_domain_ids = fields.Char(string="Domain Ids")
    code_domain_ids = fields.Char(string="Code Domain Ids")
    catalog_id = fields.Many2one(
        'ecosystem.ecologic.catalog',
        string='Product to Repair',
        required=False,
    )
    catalog_catalog_id = fields.Many2one(
        'catalog.catalog',
        string='Product to Repair',
        required=False,
        domain="[('is_available_for_repair', '=', True)]"
    )
    other_product_to_repair = fields.Boolean(
        string='Other Product',
        required=False,
        help='Product not in the pre-defined list'
    )
    is_phone_case = fields.Boolean(
        string='Phone Case is left',
        required=False,
    )
    is_cable = fields.Boolean(
        string='Cable is left',
        required=False,
    )
    complement_repair_product = fields.Char(
        string='Complement Repair Product',
        required=False,
    )

    device_type = fields.Selection(
        [
            ('laptop', 'Laptop'),
            ('smartphone', 'Smartphone'),
            ('smartwatch', 'Smartwatch'),
            ('tablet', 'Tablet'),
        ],
        string='Device type',
        compute='_compute_device_type',
        store=True,
        readonly=True,
    )

    @api.depends('catalog_catalog_id')
    def _compute_device_type(self):
        """Compute device_type based on the selected catalog"""
        # Mapping of catalog names to device_type values
        catalog_mapping = {
            'smartwatch': 'smartwatch',
            'smartphone': 'smartphone',
            'laptop': 'laptop',
            'tablette': 'tablet',  # French name for tablet
            'tablet': 'tablet',     # English variant
        }
        
        for repair in self:
            repair.device_type = False
            if repair.catalog_catalog_id:
                catalog_name = repair.catalog_catalog_id.name.lower().strip()
                # Try direct mapping
                if catalog_name in catalog_mapping:
                    repair.device_type = catalog_mapping[catalog_name]
                else:
                    # Fallback: check for partial matches
                    for key, value in catalog_mapping.items():
                        if key in catalog_name:
                            repair.device_type = value
                            break

    device_capacity_id = fields.Many2one(
        'device.capacity',
        string='Capicity',
        required=False,
        domain="[('device_type', '=', device_type)]"
    )

    device_color_id = fields.Many2one(
        'device.color',
        string='Color',
        required=False,
        domain="[('device_type', '=', device_type)]"
    )

    commercial_reference = fields.Char('Commercial Reference', copy=False)

    is_phone = fields.Boolean('Is Phone ?', compute='_set_is_phone')

    def normalize(self, text):
        # Remove accents
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        # Lowercase
        text = text.lower()
        # Remove special characters (keep letters and spaces)
        text = re.sub(r'[^a-z\s]', ' ', text)
        return text
        
    @api.depends('catalog_catalog_id')
    def _set_is_phone(self):
        for repair in self:
            repair.is_phone = False
            if repair.catalog_catalog_id and ("telephone" in self.normalize(repair.catalog_catalog_id.name) and "portable" in self.normalize(repair.catalog_catalog_id.name)):
                repair.is_phone = True

    product_to_repair_type = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='product to repair type',
        compute='_compute_product_to_repair_type'
    )

    @api.depends('brand_brand_id')
    def _compute_product_to_repair_type(self):
        for repair in self:
            repair.product_to_repair_type = repair.brand_brand_id.brand_type

    @api.onchange('catalog_id')
    def _get_catalog_brands(self):
        if self.catalog_id:
            # Build domain based on the parent_id
            code_domain = [('catalog_id', '=', self.catalog_id.id)]
            brand_domain = [('brand_type', '=', self.catalog_id.catalog_type)]
            # Search for the records that match the domain
            if self.catalog_id.catalog_type == 'ecosystem':
                brand_domain.append(('catalog_id', '=', self.catalog_id.id))
            code_records = self.env['repair.code'].search(code_domain)
            brand_records = self.env['repair.brand'].search(brand_domain)
            # Store the ids in the helper field
            self.catalog_domain_ids = [('id', 'in', brand_records.ids)]
            self.code_domain_ids = [('id', 'in', code_records.ids)]
        else:
            self.catalog_domain_ids = [('id', '=', 0)]
            self.code_domain_ids = [('id', '=', 0)]

    repair_code_id = fields.Many2one(
        'repair.code',
        string='Code',
        required=False,
        domain=code_domain_ids,
        copy=False
    )
    
    repair_brand_id = fields.Many2one(
        'repair.brand',
        string='Brand',
        required=False,
        domain=catalog_domain_ids,
        copy=False
    )

    code_code_id = fields.Many2one(
        'code.code',
        string='Code',
        required=False,
        copy=False
    )
    
    brand_brand_id = fields.Many2one(
        'brand.brand',
        string='Brand',
        required=False,
        copy=False,
        domain="[('is_available_for_repair', '=', True)]"
    )

    commercial_reference_id = fields.Many2one(
        'commercial.reference',
        string='Commercial Reference',
        required=False,
        copy=False,
        domain="[('brand_brand_id', '=', brand_brand_id)]"
    )

    device_id = fields.Char('Device ID', required=False, copy=False)
    # repair_device_id = fields.Many2one(
    #     'repair.device',
    #     string='Device',
    #     required=False,
    #     copy=False
    # )
    
    # repair_model_id = fields.Many2one(
    #     'repair.model',
    #     string='Model',
    #     required=False,
    #     copy=False
    # )
    assigned_technician = fields.Many2one('hr.employee', 'Assigned Technician', copy=False)
    unlock_code = fields.Char('Unlock code', copy=False)
    if_eligible = fields.Boolean('QualiRépar eligible', copy=False)
    nameplate_photo = fields.Image('Photo of the nameplate', copy=False)
    # repaired_product_photo = fields.Image('Photos of the repaired product', copy=False)
    
    # ecologic fields
    piece_of_evidence_file = fields.Binary(string='Piece of evidence', copy=False)
    piece_of_evidence_filename = fields.Char(string='File Name', store=True, copy=False)
    claim_id = fields.Char('Claim ID', readonly=True, copy=False)
    is_valid = fields.Boolean('Is valid', readonly=True, copy=False)
    is_submitted = fields.Boolean('Is Submitted', readonly=True, copy=False)
    invoice_uploaded = fields.Boolean('Is Invoice File uploaded ?', readonly=True, copy=False)
    name_plate_uploaded = fields.Boolean('Is Nameplate File uploaded ?', readonly=True, copy=False)
    device_picture_uploaded = fields.Boolean('Is Device Picture File uploaded ?', readonly=True, copy=False)
    piece_of_evidence_uploaded = fields.Boolean('Is piece of evidence File uploaded ?', readonly=True, copy=False)

    failure_description = fields.Char('Failure Description', copy=False)
    iris_section = fields.Char('IRIS Section', help='The IRIS breakdown code must be included among those associated with the product in the repository.', copy=False, compute='_compute_iris_section')

    claim_creation_date = fields.Date(
        string='Claim Creation Date',
        store=True,
        readonly=True,
    )

    claim_organization = fields.Selection(
        [
            ('ecosystem', 'Ecosystem'),
            ('ecologic', 'Ecologic'),
        ],
        string='Concerned Organization',
        copy=False, readonly=True, tracking=True,
    )

    eventual_comments = fields.Html(
        string="Eventual Comments",
        sanitize_style=True,
        readonly=False,
    )

    @api.depends('code_code_id')
    def _compute_iris_section(self):
        for repair in self:
            repair.iris_section = ''
            if repair.code_code_id:
                name_value = '%' + repair.code_code_id.name[1:]
                repair_code_id = self.env['repair.code'].search([('name', 'ilike', name_value), ('code_type', '=', 'ecologic')])
                repair.iris_section = repair_code_id[0].code

    repair_end_date = fields.Datetime('Repair end date', readonly=True, store=True)

    accessories_ids = fields.Many2many('accessories.provided', string='Accessories Provided')

    # Irreparability certificate fields
    motif_irreparabilite = fields.Selection(
        [
            ('oxidation_severe', 'Oxydation sévère'),
            ('pieces_obsoletes', 'Pièces obsolètes'),
            ('cout_reparation', 'Coût de réparation > Valeur appareil'),
            ('autre', 'Autre'),
        ],
        string='Motif de l\'irréparabilité',
        copy=False,
        tracking=True,
    )
    motif_irreparabilite_autre = fields.Text(
        string='Précisions sur le motif',
        copy=False,
    )
    date_certificat_irreparabilite = fields.Datetime(
        string='Date du certificat d\'irréparabilité',
        readonly=True,
        copy=False,
    )

    # ecosystem extra fields
    reimbursement_claim_id = fields.Char('Reimbursement Claim ID', readonly=True, copy=False)
    sap_service_order = fields.Char('Sap Service Order', readonly=True, copy=False)
    ecosystem_request_status = fields.Char('Ecosystem Request Status', readonly=True, copy=False)
    invoice_file_uploaded = fields.Boolean('Is Invoice uploaded ?', readonly=True, copy=False)
    serial_tag_file_uploaded = fields.Boolean('Is Serial Tag uploaded ?', readonly=True, copy=False)
    claim_request_file_uploaded = fields.Boolean('Is Claim Request File uploaded ?', readonly=True, copy=False)
    device_picture_file_uploaded = fields.Boolean('Is Device Picture File uploaded ?', readonly=True, copy=False)

    is_claim_created = fields.Boolean('Is claim created ?', compute="_check_claim_status", copy=False)
    is_claim_confirmed = fields.Boolean('Is claim confirmed ?', compute="_check_claim_status_1", copy=False)

    is_claim_confirmed_and_verified = fields.Boolean('Is claim confirmed and verified ?', readonly=True, copy=False)

    reimbursement_claim_state = fields.Selection(
        [
            ('draft', 'New Request'),
            ('sent', 'Request Sent'),
            ('file_uploaded', 'Files Uploaded'),
            ('confirmed', 'Request Confirmed'),
            ('done', 'Done'),
        ],
        string='Reimbursement Status',
        copy=False, default='draft', readonly=True, tracking=True, index=True,
    )

    @api.depends('reimbursement_claim_id', 'claim_id')
    def _check_claim_status(self):
        for repair in self:
            repair.is_claim_created = False
            if repair.reimbursement_claim_id and repair.product_to_repair_type == 'ecosystem':
                repair.is_claim_created = True
            elif repair.claim_id and repair.product_to_repair_type == 'ecologic':
                repair.is_claim_created = True

    @api.depends('sap_service_order')
    def _check_claim_status_1(self):
        for repair in self:
            repair.is_claim_confirmed = False
            if repair.sap_service_order:
                repair.is_claim_confirmed = True

    are_files_uploaded = fields.Boolean('Are files uploaded ?', compute="_check_files", copy=False)

    @api.depends(
        'invoice_file_uploaded', 
        'serial_tag_file_uploaded', 
        'claim_request_file_uploaded', 
        'device_picture_file_uploaded',
        'invoice_uploaded',
        'name_plate_uploaded',
        'piece_of_evidence_uploaded'
    )
    def _check_files(self):
        for repair in self:
            repair.are_files_uploaded = False
            if repair.product_to_repair_type == 'ecosystem' and any(elem for elem in [repair.invoice_file_uploaded, repair.serial_tag_file_uploaded, repair.claim_request_file_uploaded, repair.device_picture_file_uploaded]):
                repair.are_files_uploaded = True
            elif repair.product_to_repair_type == 'ecologic' and all(elem for elem in [repair.invoice_uploaded, repair.name_plate_uploaded, repair.piece_of_evidence_uploaded]):
                repair.are_files_uploaded = True
            else:
                continue

    # prices
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True,
        precompute=True,
        ondelete='restrict'
    )

    currency_rate = fields.Float(
        string="Currency Rate",
        compute='_compute_currency_rate',
        digits=0,
        store=True, precompute=True)

    @api.depends('company_id')
    def _compute_currency_id(self):
        for repair in self:
            repair.currency_id = repair.company_id.currency_id

    @api.depends('currency_id', 'create_date', 'company_id')
    def _compute_currency_rate(self):
        for repair in self:
            repair.currency_rate = self.env['res.currency']._get_conversion_rate(
                from_currency=repair.company_id.currency_id,
                to_currency=repair.currency_id,
                company=repair.company_id,
                date=(repair.create_date or fields.Datetime.now()).date(),
            )

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
            "The default value comes from the customer.",
    )

    show_update_fpos = fields.Boolean(
        string="Has Fiscal Position Changed", store=False)  # True if the fiscal position was changed

    @api.onchange('fiscal_position_id')
    def _onchange_fpos_id_show_update_fpos(self):
        if self.move_ids and (
            not self.fiscal_position_id
            or (self.fiscal_position_id and self._origin.fiscal_position_id != self.fiscal_position_id)
        ):
            self.show_update_fpos = True
    
    def action_update_taxes(self):
        self.ensure_one()

        self._recompute_taxes()

        if self.partner_id:
            self.message_post(body=_("Product taxes have been recomputed according to fiscal position %s.",
                self.fiscal_position_id._get_html_link() if self.fiscal_position_id else "")
            )

    def _recompute_taxes(self):
        lines_to_recompute = self.move_ids
        lines_to_recompute._compute_tax_id()
        self.show_update_fpos = False

    @api.depends('partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for repair in self:
            if not repair.partner_id:
                repair.fiscal_position_id = False
                continue
            fpos_id_before = repair.fiscal_position_id.id
            key = (repair.company_id.id, repair.partner_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    repair.company_id
                )._get_fiscal_position(repair.partner_id).id
            if fpos_id_before != cache[key] and repair.move_ids:
                repair.show_update_fpos = True
            repair.fiscal_position_id = cache[key]

    def action_validate_repair(self):
        for repair in self:
            next_state = self.env['repair.state'].search(
                [('sequence', '=', repair.state_id.sequence + 1)],
                limit=1
            )
            if repair.state_id.sequence == 1:
                # check if serial tag is required
                if repair.product_to_repair_type == 'ecosystem':
                    real_catalog = self.env['ecosystem.ecologic.catalog'].search([('name', '=', repair.catalog_catalog_id.name), ('catalog_type', '=', 'ecosystem')], limit=1)
                    if real_catalog.is_serial_tag_required and not repair.nameplate_photo:
                        raise ValidationError(_('The Nameplate Photo of this Catalog must be specified !'))

            if repair.state_id.sequence == 2:
                # check if there is no SO
                if not repair.sale_order_id:
                    raise ValidationError(_('The sale order must be created !'))
                
            repair.write({'state_id': next_state.id})

    # TODO: separate get token request
    def action_create_new_claim(self):
        for repair in self:
            base_url = request.httprequest.host_url
            # base_url = request.httprequest.host_url.replace("http://", "https://")
            invoice = repair.sale_order_id.invoice_ids[0]
            if repair.product_to_repair_type == 'ecosystem':
                login_api_endpoint = 'api/login'
                login_api_url = base_url + login_api_endpoint
                response = requests.post(login_api_url, json={}, timeout=30)
                if response.status_code == 200:
                    result_login = response.json()  # Parse the JSON response
                else:
                    raise ValidationError(_("Login API error: %s") % response.text)
                if 'error' in result_login['result']:
                    raise ValidationError(_("No token gotten \n - Code: %s \n - Status: %s \n - Message: %s") 
                        % (
                            result_login['result']['error']['code'], 
                            result_login['result']['error']['status'], 
                            result_login['result']['error']['message']
                        )
                    )
                token = result_login['result']['IdToken']
                # call new_claim route
                repairer_id = result_login['result']['AllowedRepairer'][0]
                new_claim_endpoint = 'api/new_claim'
                new_claim_url = base_url + new_claim_endpoint
                if any(not info for info in [repair.partner_id.email, repair.partner_id.street, repair.partner_id.phone, repair.partner_id.zip, repair.partner_id.city, repair.partner_id.country_code]):
                    raise ValidationError(_('Some customer info missing !'))
                contact_title_0 = ''
                if repair.partner_id.is_company:
                    contact_title_0 = 'Autre'
                else:
                    if repair.partner_id.contact_title == '1':
                        contact_title_0 = 'M.'
                    elif repair.partner_id.contact_title == '2':
                        contact_title_0 = 'Mme.'
                real_catalog = self.env['ecosystem.ecologic.catalog'].search([('name', '=', repair.catalog_catalog_id.name), ('catalog_type', '=', 'ecosystem')], limit=1)
                real_brand = self.env['repair.brand'].search([('name', '=', repair.brand_brand_id.name), ('brand_type', '=', 'ecosystem')], limit=1)
                code_name_value = '%' + repair.code_code_id.name[1:]
                repair_code_id = self.env['repair.code'].search([('name', 'ilike', code_name_value), ('code_type', '=', 'ecosystem')])
                payload_vals = {
                    'token': token,
                    'PurchaseOrderByCustomer': repair.name,
                    'RepairDate': repair.create_date.strftime('%Y-%m-%d'),
                    'RepairPlaceID': '2000000',
                    'RepairerId': repairer_id,
                    'Product': {
                        'ProductID': real_catalog.product_id,
                        'BrandID': real_brand.brand_id,
                        'ProductIdentificationNumber': repair.device_id,
                        'RepairTypeCode': repair_code_id[0].code,
                        'IrisCode' : 'MyIrisCode',
                        'CommercialReference': repair.commercial_reference_id.name if repair.commercial_reference_id else '',
                    },
                    'Customer': {
                        'Title': contact_title_0,
                        'LastName': str(repair.partner_id.name).split(' ')[1] if len(str(repair.partner_id.name).split(' ')) > 1 else 'empty',
                        'FirstName': str(repair.partner_id.name).split(' ')[0] or 'empty',
                        'Email': repair.partner_id.email,
                        'PhoneNumber': str(repair.partner_id.phone).replace(' ', '').replace('+33', '0'),
                        'StreetLine1': repair.partner_id.street,
                        'PostalCode': repair.partner_id.zip,
                        'City': repair.partner_id.city,
                        'Country': repair.partner_id.country_code
                    },
                    'Bill': {
                        'TotalAmountInclVAT': {
                            'amount': invoice.amount_total,
                            'currency': 'EUR'
                        },
                        'AmountCovered': {
                            'amount': 25.00 if invoice.amount_total > 25 else 0,
                            'currency': 'EUR'
                        }
                    }
                }
                response = requests.post(new_claim_url, json=payload_vals, timeout=30)
                if response.status_code == 200:
                    result_new_claim = response.json()  # Parse the JSON response
                else:
                    result_new_claim = response.text
                    raise ValidationError(_('Error encoutered : %s') % result_new_claim)
                if 'error' in result_new_claim['result']:
                    raise ValidationError(_("Claim not created \n - Code: %s \n - Status: %s \n - Message: %s") 
                        % (
                            result_new_claim['result']['error']['code'], 
                            result_new_claim['result']['error']['status'], 
                            result_new_claim['result']['error']['message']
                        )
                    )
                logging.info('response : {}'.format(result_new_claim))
                if 'result' in result_new_claim:
                    repair.write({
                        'reimbursement_claim_id': result_new_claim['result']['ReimbursementClaimID'],
                        'ecosystem_request_status': result_new_claim['result']['RequestStatus'],
                        'reimbursement_claim_state': 'sent',
                        'claim_creation_date': fields.Datetime.now().date()
                    })
            elif repair.product_to_repair_type == 'ecologic':
                ecologic_claim_endpoint = 'api/create_claim'
                ecologic_claim_url = base_url + ecologic_claim_endpoint
                if any(not info for info in [repair.partner_id.email, repair.partner_id.street, repair.partner_id.phone, repair.partner_id.zip, repair.partner_id.city]):
                    raise ValidationError(_('Some customer info missing !'))
                contact_title = int()
                if repair.partner_id.is_company:
                    contact_title = 4
                else:
                    if repair.partner_id.contact_title == '1':
                        contact_title = 1
                    elif repair.partner_id.contact_title == '1':
                        contact_title = 3
                real_catalog = self.env['ecosystem.ecologic.catalog'].search([('name', '=', repair.catalog_catalog_id.name), ('catalog_type', '=', 'ecologic')], limit=1)
                real_brand = self.env['repair.brand'].search([('name', '=', repair.brand_brand_id.name), ('brand_type', '=', 'ecologic')], limit=1)
                payload_vals = {
                    'Consumer': {
                        'Title': contact_title,
                        'LastName': str(repair.partner_id.name).split(' ')[1] if len(str(repair.partner_id.name).split(' ')) > 1 else 'empty',
                        'FirstName': str(repair.partner_id.name).split(' ')[0] or 'empty',
                        'StreetNumber': '',
                        'Address1': repair.partner_id.street,
                        'Address2': '',
                        'Address3': '',
                        'Zip': repair.partner_id.zip,
                        'City': repair.partner_id.city,
                        'Country': '250', # France
                        'Phone': str(repair.partner_id.phone).replace(' ', '').replace('+33', '0'),
                        'Email': repair.partner_id.email  
                    },
                    'Product': {
                        'ProductId': real_catalog.product_id,
                        'BrandId': real_brand.brand_id,
                        'CommercialRef': repair.commercial_reference_id.name if repair.commercial_reference_id else '',
                        'SerialNumber': repair.device_id,
                        'PurchaseDate': '',
                        'IRISCondition': '',
                        'IRISConditionEX': '',
                        'IRISSymptom': '',
                        'IRISSection': repair.iris_section,
                        'IRISDefault': '',
                        'IRISRepair': '',
                        'FailureDescription': repair.failure_description,
                        'DefectCode': ''  
                    },
                    'Quote': {
                        'TotalAmountInclVAT': {
                            'Amount': invoice.amount_total,
                            'Currency': 'EUR'
                        },
                        'SupportAmount': {
                            'Amount': 25.00 if invoice.amount_total > 25 else 0,
                            'Currency': 'EUR'
                        }
                    }
                }
                dt = repair.repair_end_date
                user_tz = self.env.user.tz or self.env.context.get('tz')
                user_pytz = pytz.timezone(user_tz) if user_tz else pytz.utc
                repair_end_date = dt and dt.astimezone(user_pytz).strftime('%Y-%m-%dT%H:%M:%SZ') or None
                consumer_invoice_number = repair.sale_order_id.invoice_ids[0].name
                # get site ID
                get_repair_site_endpoint = 'api/get_repair_site'
                get_repair_site_url = base_url + get_repair_site_endpoint
                response = requests.get(get_repair_site_url, json={}, timeout=30)
                if response.status_code == 200:
                    result_repair_site = response.json()  # Parse the JSON response
                else:
                    raise Exception(_("Get Repair Site ID API error: %s") % response.text)
                if 'result' in result_repair_site and result_repair_site['result']['ResponseData']:
                    site_id = result_repair_site['result']['ResponseData'][0]['SiteId']
                else:
                    raise Exception(_("No Site gotten: %s") % result_repair_site)
                repair_site_id = site_id
                params = {
                    "repairEndDate": repair_end_date,
                    "repairSiteId": repair_site_id or None,
                    "consumerInvoiceNumber": consumer_invoice_number or None,
                }
                response = requests.post(ecologic_claim_url, json=payload_vals, params=params, timeout=30)
                if response.status_code == 200:
                    result_ecologic_claim = response.json()  # Parse the JSON response
                else:
                    result_ecologic_claim = response.text
                    raise ValidationError('Error encoutered : {}'.format(result_ecologic_claim))
                logging.info('respose : {}'.format(result_ecologic_claim))
                if 'result' in result_ecologic_claim:
                    repair.write({
                        'claim_id': result_ecologic_claim['result']['ResponseData']['ClaimId'],
                        'is_valid': result_ecologic_claim['result']['ResponseData']['IsValid'],
                        'reimbursement_claim_state': 'sent',
                        'claim_creation_date': fields.Datetime.now().date()
                    })
                    if 'ValidationErrors' in result_ecologic_claim['result']['ResponseData'] and result_ecologic_claim['result']['ResponseData']['ValidationErrors']:
                        result = ""
                        for error in result_ecologic_claim['result']['ResponseData']['ValidationErrors']:
                            result += "- " + error['Field'] + ": " + error['ErrorMessage'] + "\n\n"
                        return {
                            "name": _("API Response"),
                            "type": "ir.actions.act_window",
                            "res_model": "api.response",
                            "view_mode": "form",
                            "views": [[False, "form"]],
                            "target": "new",
                            "context": {'default_result_message': result},
                        }
            else:
                continue

    ### HELPERS
    # Ecosystem flow

    def _upload_ecosystem_files(self, repair, base_url):
        token = self._ecosystem_login(base_url)
        upload_files_data = self._prepare_ecosystem_files(repair)
        if not upload_files_data:
            return
        upload_url = base_url + 'api/reimbursement_claims/upload_file'
        all_files_uploaded = True
        for file in upload_files_data:
            self._ecosystem_upload_single_file(
                repair, token, upload_url, file
            )
        if all_files_uploaded:
            repair.write({'reimbursement_claim_state': 'file_uploaded'})

    def _ecosystem_login(self, base_url):
        response = requests.post(base_url + 'api/login', json={}, timeout=30)
        if response.status_code != 200:
            raise Exception(_("Login API error: %s") % response.text)
        result = response.json()
        token = result.get('result', {}).get('IdToken')
        if not token:
            raise Exception(_("No token gotten: %s") % result)
        return token

    def _prepare_ecosystem_files(self, repair):
        files = []
        real_catalog = self.env['ecosystem.ecologic.catalog'].search([
            ('name', '=', repair.catalog_catalog_id.name),
            ('catalog_type', '=', 'ecosystem')
        ], limit=1)
        # Serial tag
        if real_catalog.is_serial_tag_required and repair.nameplate_photo:
            decoded = base64.b64decode(repair.nameplate_photo)
            file_type = imghdr.what(None, decoded)
            if file_type:
                files.append({
                    'FileName': f'image.{file_type}',
                    'FileType': 'serial_tag',
                    'FileSizeInMB': round(len(decoded) / (1024 * 1024), 2),
                    'FileFormat': file_type,
                    'RawFile': decoded,
                })
        # Invoice
        if not repair.sale_order_id or not repair.sale_order_id.invoice_ids:
            raise ValidationError(_('No invoice related to this repair order !'))
        invoice = repair.sale_order_id.invoice_ids[0]
        invoice_info = invoice._get_invoice_legal_documents('pdf', True)
        files.append({
            'FileName': 'invoice.pdf',
            'FileType': 'invoice',
            'FileSizeInMB': round(len(invoice_info['content']) / (1024 * 1024), 2),
            'FileFormat': 'pdf',
            'RawFile': invoice_info['content'],
        })
        return files

    def _ecosystem_upload_single_file(self, repair, token, upload_url, file):
        payload = {
            'token': token,
            'ReimbursementClaimID': repair.reimbursement_claim_id,
            'FileName': file['FileName'],
            'FileType': file['FileType'],
            'FileSizeInMB': file['FileSizeInMB'],
        }
        response = requests.post(upload_url, json=payload, timeout=30)
        if response.status_code != 200:
            raise ValidationError(_('Upload error: %s') % response.text)
        result = response.json().get('result')
        if not result:
            raise ValidationError(_('Invalid upload response'))
        headers = {
            "Content-Type": (
                "application/pdf"
                if file['FileFormat'] == 'pdf'
                else f"image/{file['FileFormat']}"
            )
        }
        put_response = requests.put(
            result['url'],
            headers=headers,
            data=file['RawFile'],
            timeout=30
        )
        if put_response.status_code != 200:
            raise ValidationError(_('PUT error: %s') % put_response.text)
        self._set_ecosystem_file_flag(repair, file['FileType'])

    def _set_ecosystem_file_flag(self, repair, file_type):
        mapping = {
            'invoice': 'invoice_file_uploaded',
            'serial_tag': 'serial_tag_file_uploaded',
            'claim_request': 'claim_request_file_uploaded',
            'device_picture': 'device_picture_file_uploaded',
        }
        field = mapping.get(file_type)
        if field:
            repair.write({field: True})

    # Ecologic flow
    def _upload_ecologic_files(self, repair, base_url):
        files = self._prepare_ecologic_files(repair)
        if not files:
            return
        upload_url = base_url + 'api/attach_file'
        for file in files:
            self._ecologic_upload_single_file(repair, upload_url, file)
        repair.write({'reimbursement_claim_state': 'file_uploaded'})

    def _prepare_ecologic_files(self, repair):
        files = []
        if repair.nameplate_photo:
            decoded = base64.b64decode(repair.nameplate_photo)
            file_type = imghdr.what(None, decoded)
            if file_type:
                files.append({
                    'filename': f'image1.{file_type}',
                    'documentType': 'NAMEPLATE',
                    'fileextension': file_type,
                    'FileContent': repair.nameplate_photo.decode('utf-8'),
                })
        if repair.piece_of_evidence_file:
            files.append({
                'filename': 'piece_of_evidence.pdf',
                'documentType': 'CONSUMERVALIDATION',
                'fileextension': 'pdf',
                'FileContent': base64.b64encode(
                    repair.piece_of_evidence_file
                ).decode('utf-8'),
            })
        if not repair.sale_order_id or not repair.sale_order_id.invoice_ids:
            raise ValidationError(_('No invoice related to this repair order !'))
        invoice = repair.sale_order_id.invoice_ids[0]
        invoice_info = invoice._get_invoice_legal_documents('pdf', True)
        files.append({
            'filename': 'invoice.pdf',
            'documentType': 'INVOICE',
            'fileextension': 'pdf',
            'FileContent': base64.b64encode(
                invoice_info['content']
            ).decode('utf-8'),
        })
        return files

    def _ecologic_upload_single_file(self, repair, upload_url, file):
        response = requests.post(
            upload_url,
            json={'FileContent': file['FileContent']},
            params={
                'ClaimId': repair.claim_id,
                'filename': file['filename'],
                'fileextension': file['fileextension'],
                'documentType': file['documentType'],
            },
            timeout=30
        )
        if response.status_code != 200:
            raise ValidationError(_('Upload error: %s') % response.text)
        if 'result' not in response.json():
            raise ValidationError(_('Invalid upload response'))
        self._set_ecologic_file_flag(repair, file['documentType'])

    def _set_ecologic_file_flag(self, repair, document_type):
        mapping = {
            'INVOICE': 'invoice_uploaded',
            'NAMEPLATE': 'name_plate_uploaded',
            'PRODUCTPICTURE': 'device_picture_uploaded',
            'CONSUMERVALIDATION': 'piece_of_evidence_uploaded',
        }
        field = mapping.get(document_type)
        if field:
            repair.write({field: True})

    # mqin action
    def action_claim_upload_file(self):
        base_url = request.httprequest.host_url
        # base_url = request.httprequest.host_url.replace("http://", "https://")
        for repair in self:
            if repair.product_to_repair_type == 'ecosystem':
                self._upload_ecosystem_files(repair, base_url)

            elif repair.product_to_repair_type == 'ecologic':
                self._upload_ecologic_files(repair, base_url)

    def action_confirm_claim(self):
        for repair in self:
            login_api_endpoint = 'api/login'
            base_url = request.httprequest.host_url
            # base_url = request.httprequest.host_url.replace("http://", "https://")
            login_api_url = base_url + login_api_endpoint
            response = requests.post(login_api_url, json={}, timeout=30)
            if response.status_code == 200:
                result_login = response.json()  # Parse the JSON response
            else:
                raise Exception(_("Login API error: %s") % response.text)
            if 'error' in result_login['result']:
                raise ValidationError(_("No token gotten \n - Code: %s \n - Status: %s \n - Message: %s") 
                    % (
                        result_login['result']['error']['code'], 
                        result_login['result']['error']['status'], 
                        result_login['result']['error']['message']
                    )
                )
            token = result_login['result']['IdToken']
            # call confirm claim route
            confirm_claim_endpoint = 'api/reimbursement_claims/confirm_claim'
            confirm_claim_url = base_url + confirm_claim_endpoint
            payload_vals = {
                'token': token,
                'ReimbursementClaimID': repair.reimbursement_claim_id,
            }
            response = requests.post(confirm_claim_url, json=payload_vals, timeout=30)
            if response.status_code == 200:
                result_confirm_claim = response.json()  # Parse the JSON response
            else:
                result_confirm_claim = response.text
                raise ValidationError(_('Error encoutered : %s') % result_confirm_claim)
            if 'error' in result_confirm_claim['result']:
                raise ValidationError(_("Error encoutered \n - Code: %s \n - Status: %s \n - Message: %s") 
                    % (
                        result_confirm_claim['result']['error']['code'], 
                        result_confirm_claim['result']['error']['status'], 
                        result_confirm_claim['result']['error']['message']
                    )
                )
            logging.info('respose : {}'.format(result_confirm_claim))
            repair.write({
                # 'reimbursement_claim_id': result_confirm_claim['result']['SapServiceOrder'],
                'sap_service_order': result_confirm_claim['result']['SapServiceOrder'],
                'ecosystem_request_status': result_confirm_claim['result']['RequestStatus'],
                'reimbursement_claim_state': 'confirmed'
            })

    def action_get_one_claim(self):
        for repair in self:
            login_api_endpoint = 'api/login'
            base_url = request.httprequest.host_url
            # base_url = request.httprequest.host_url.replace("http://", "https://")
            login_api_url = base_url + login_api_endpoint
            response = requests.post(login_api_url, json={}, timeout=30)
            if response.status_code == 200:
                result_login = response.json()  # Parse the JSON response
            else:
                raise Exception(_("Login API error: %s") % response.text)
            if 'error' in result_login['result']:
                raise ValidationError(_("No token gotten \n - Code: %s \n - Status: %s \n - Message: %s") 
                    % (
                        result_login['result']['error']['code'], 
                        result_login['result']['error']['status'], 
                        result_login['result']['error']['message']
                    )
                )
            token = result_login['result']['IdToken']
            # call get one claim route
            get_one_claim_endpoint = 'api/reimbursement_claims/get_one_claim'
            cget_one_claim_url = base_url + get_one_claim_endpoint
            payload_vals = {
                'token': token,
                'ReimbursementClaimID': repair.reimbursement_claim_id,
            }
            response = requests.get(cget_one_claim_url, json=payload_vals, timeout=30)
            if response.status_code == 200:
                result_get_one_claim = response.json()  # Parse the JSON response
            else:
                result_get_one_claim = response.text
                raise ValidationError(_('Error encoutered : %s') % result_get_one_claim)
            if 'error' in result_get_one_claim['result']:
                raise ValidationError(_("Error encoutered \n - Code: %s \n - Status: %s \n - Message: %s") 
                    % (
                        result_get_one_claim['result']['error']['code'], 
                        result_get_one_claim['result']['error']['status'], 
                        result_get_one_claim['result']['error']['message']
                    )
                )
            logging.info('response : {}'.format(result_get_one_claim))
            if str(repair.ecosystem_request_status).strip() == str(result_get_one_claim['result']['Items'][0]['RequestStatus']).strip():
                continue
            repair.write({
                'ecosystem_request_status': result_get_one_claim['result']['Items'][0]['RequestStatus'],
                'is_claim_confirmed_and_verified': True,
            })

    def action_get_claim_status_ecologic(self):
        """ Check Claim Status Ecologic """
        for repair in self:
            base_url = request.httprequest.host_url
            # base_url = request.httprequest.host_url.replace("http://", "https://")
            get_claim_status_endpoint = 'api/get_claim_status'
            get_claim_status_url = base_url + get_claim_status_endpoint
            params = {
                'ClaimId': repair.claim_id,
            }
            response = requests.get(get_claim_status_url, json={}, params=params, timeout=30)
            if response.status_code == 200:
                result_get_claim_status = response.json()  # Parse the JSON response
            else:
                result_get_claim_status = response.text
                raise ValidationError(_('Error encoutered : %s') % result_get_claim_status)
            logging.info('response : {}'.format(result_get_claim_status))
            if 'result' in result_get_claim_status:
                if 'ValidationErrors' not in result_get_claim_status['result']['ResponseData'] or result_get_claim_status['result']['ResponseData']['ValidationErrors'] == []:
                    repair.write({
                        'is_valid': True,
                    })
                else:
                    result = ""
                    for error in result_get_claim_status['result']['ResponseData']['ValidationErrors']:
                        result += "- " + error['Field'] + ": " + error['ErrorMessage'] + "\n\n"
                    return {
                        "name": _("API Response"),
                        "type": "ir.actions.act_window",
                        "res_model": "api.response",
                        "view_mode": "form",
                        "views": [[False, "form"]],
                        "target": "new",
                        "context": {'default_result_message': result},
                    }

    def action_submit_claim_ecologic(self):
        """ Submit Claim Ecologic """
        for repair in self:
            base_url = request.httprequest.host_url
            # base_url = request.httprequest.host_url.replace("http://", "https://")
            submit_claim_endpoint = 'api/submit_claim'
            submit_claim_url = base_url + submit_claim_endpoint
            params = {
                'ClaimId': repair.claim_id,
            }
            response = requests.post(submit_claim_url, json={}, params=params, timeout=30)
            if response.status_code == 200:
                result_submit_claim = response.json()  # Parse the JSON response
            else:
                result_submit_claim = response.text
                raise ValidationError(_('Error encoutered : %s') % result_submit_claim)
            logging.info('response : {}'.format(result_submit_claim))
            if 'result' in result_submit_claim:
                if result_submit_claim['result']['ResponseData']['IsValid']:
                    repair.write({
                        'is_submitted': True,
                        'reimbursement_claim_state': 'confirmed'
                    })
                else:
                    raise ValidationError(_('Not submitted, reason : %s') % result_submit_claim['result']['ResponseData']['LastStatus'])

    show_customer_info_alert = fields.Boolean(compute='_compute_show_customer_info_alert', store=True)
    customer_info_alert_message = fields.Char(compute='_compute_show_customer_info_alert', store=True)

    @api.depends(
        'if_eligible',
        'partner_id',
        'partner_id.street',
        'partner_id.city',
        'partner_id.zip',
        'partner_id.contact_title',
        'partner_id.phone',
        'partner_id.email',
    )
    def _compute_show_customer_info_alert(self):
        for repair in self:
            repair.show_customer_info_alert = False
            repair.customer_info_alert_message = False
            if not repair.if_eligible:
                continue
            repair.show_customer_info_alert = True
            # No customer selected
            if not repair.partner_id:
                repair.customer_info_alert_message = (
                    _("Customer is missing !")
                )
                continue
            partner = repair.partner_id
            missing_fields = []
            if not partner.street:
                missing_fields.append(_("Street"))
            if not partner.city:
                missing_fields.append(_("City"))
            if not partner.zip:
                missing_fields.append(_("Postal Code"))
            if not partner.contact_title:
                missing_fields.append(_("Title"))
            if not partner.phone:
                missing_fields.append(_("Phone"))
            if not partner.email:
                missing_fields.append(_("Email"))
            if missing_fields:
                repair.customer_info_alert_message = (
                    _("Missing customer info : %s")
                    % ", ".join(missing_fields)
                )
            else:
                repair.show_customer_info_alert = False

    state_id = fields.Many2one(
        'repair.state', string='State', index=True, tracking=True,
        readonly=False, store=True,
        copy=False, ondelete='restrict',
        default=lambda self: self._default_state()
    )

    state_ids = fields.Many2many(
        'repair.state.helper', 
        'repair_state_helper_rel',
        string='State',
        compute='_set_state_helper'
    )

    @api.depends('state_id')
    def _set_state_helper(self):
        for record in self:
            state_id = self.env['repair.state.helper'].search([('sequence', '=', record.state_id.sequence)], limit=1)
            record.state_ids = [(6, 0, [state_id.id])]

    @api.model
    def _default_state(self):
        return self.env['repair.state'].search([], order='sequence', limit=1)

    def _get_uto_repair_sequence(self, company=None):
        company = company or self.env.company
        seq = self.env['ir.sequence'].search([
            ('code', '=', 'repair.order.uto'),
            ('company_id', '=', company.id)
        ], limit=1)
        if not seq:
            template = self.env.ref('uto_repair.seq_repair_order', raise_if_not_found=False)
            if template:
                seq = template.sudo().copy({'company_id': company.id})
            else:
                seq = self.env['ir.sequence'].sudo().create({
                    'name': 'Repair Order',
                    'code': 'repair.order.uto',
                    'prefix': 'REP-',
                    'padding': 5,
                    'company_id': company.id,
                })
        return seq

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company = self.env['res.company'].browse(
                vals.get('company_id', self.env.company.id)
            )
            sequence = self._get_uto_repair_sequence(company)
            picking_type = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', self.default_get(['picking_type_id'])['picking_type_id'])
            )
            if 'picking_type_id' not in vals:
                vals['picking_type_id'] = picking_type.id
            if not vals.get('name', False) or vals['name'] == 'New':
                vals['name'] = sequence.next_by_id()
            if not vals.get('procurement_group_id'):
                vals['procurement_group_id'] = self.env["procurement.group"].create({'name': vals['name']}).id
        return super().create(vals_list)

    @api.onchange('state_id')
    def _onchange_state_warning(self):
        for record in self:
            old_state = record._origin.state_id
            new_state = record.state_id

            # When editing an existing record only
            if not record._origin.id:
                return

            # Can not be in repaired or done state if there is no sale order
            if new_state.sequence in [5, 6] and not record.sale_order_id:
                return {
                    'warning': {
                        'title': "Sale Order",
                        'message': (
                            "Please create a sale order !"
                        ),
                    }
                }

            # OLD state is Done or Cancelled → block + warn
            if old_state and (old_state.is_done or old_state.is_cancelled):
                record.state_id = old_state
                return {
                    'warning': {
                        'title': "State locked",
                        'message': (
                            "You cannot change the state once the repair "
                            "is Done or Cancelled."
                        ),
                    }
                }

    schedule_date = fields.Datetime(required=False)
    schedule_date_date = fields.Date("Scheduled Date", default=fields.Date.today(), index=True, required=True, copy=False)

    def write(self, vals):
        # Allow forced transitions (used by buttons)
        if self.env.context.get('force_state'):
            return super().write(vals)
        if 'state_id' in vals:
            new_state = self.env['repair.state'].browse(vals['state_id'])
            for order in self:
                current_state = order.state_id
                if vals['state_id'] == 5:
                    vals['repair_end_date'] = fields.Datetime.now()
                    vals['claim_organization'] = order.product_to_repair_type
                if vals['state_id'] == 7:
                    if order.sale_order_id:
                        order.sale_order_id._action_cancel()
                        order.sale_order_id.unlink()
                if vals['state_id'] in [5, 6] and not order.sale_order_id:
                    del vals['state_id']
                    return super().write(vals)
                if current_state.is_done or current_state.is_cancelled:
                    del vals['state_id']
                    return super().write(vals)
                    # raise UserError(
                    #     "You cannot change the state once the repair is Done or Cancelled."
                    # )
                # # Prevent jumping states (must follow sequence)
                # if new_state.sequence != current_state.sequence + 1:
                #     raise UserError(
                #         "You must follow the workflow sequence. "
                #         "Skipping states is not allowed."
                #     )
        return super().write(vals)

    is_ro_done = fields.Boolean(compute="_set_values", store=True)
    is_ro_cancelled = fields.Boolean(compute="_set_values", store=True)
    is_ro_repaired = fields.Boolean(compute="_set_values", store=True)

    show_validate_button = fields.Boolean(compute="_set_values", store=True)
    show_mark_as_done_button = fields.Boolean(compute="_set_values", store=True)
    show_create_so_button = fields.Boolean(compute="_set_values", store=True)

    @api.depends('state_id')
    def _set_values(self):
        for order in self:
            # defaults
            order.is_ro_done = False
            order.is_ro_cancelled = False
            order.is_ro_repaired = False

            order.show_validate_button = False
            order.show_mark_as_done_button = False
            order.show_create_so_button = False

            if not order.state_id:
                continue

            # state flags
            if order.state_id.is_done:
                order.is_ro_done = True

            if order.state_id.is_cancelled:
                order.is_ro_cancelled = True

            if order.state_id.sequence == 5:
                order.is_ro_repaired = True

            # buttons logic
            if order.state_id.sequence in (1, 2, 3, 4):
                order.show_validate_button = True
                order.show_create_so_button = True

            elif order.state_id.sequence == 5:
                order.show_mark_as_done_button = True
                order.show_create_so_button = False

    def action_cancel_ro(self):
        cancel_state = self.env['repair.state'].search(
            [('is_cancelled', '=', True)],
            limit=1
        )
        for order in self:
            order.with_context(force_state=True).write({
                'state_id': cancel_state.id
            })
            if order.sale_order_id:
                order.sale_order_id._action_cancel()
                order.sale_order_id.unlink()

    def action_reset_to_draft_ro(self):
        draft_state = self.env['repair.state'].search(
            [('sequence', '=', 1)],
            limit=1
        )
        for order in self:
            order.with_context(force_state=True).write({
                'state_id': draft_state.id
            })

    def action_mark_as_done_repair(self):
        done_state = self.env['repair.state'].search(
            [('is_done', '=', True)],
            limit=1
        )
        for order in self:
            order.write({
                'state_id': done_state.id
            })

    def action_open_irreparability_wizard(self):
        """Ouvre le wizard pour générer le certificat d'irréparabilité"""
        self.ensure_one()
        return {
            'name': _('Générer un certificat'),
            'type': 'ir.actions.act_window',
            'res_model': 'repair.irreparability.certificate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_repair_order_id': self.id,
            }
        }

    def action_print_quotation(self):
        self.ensure_one()
        return self.env.ref('sale.action_report_saleorder').report_action(self.sale_order_id)