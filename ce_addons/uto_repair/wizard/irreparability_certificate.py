# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RepairIrrepailibilityCertificateWizard(models.TransientModel):
    _name = 'repair.irreparability.certificate.wizard'
    _description = 'Wizard to generate the irreparability certificate'

    repair_order_id = fields.Many2one(
        'repair.order',
        string='Repair Order',
        required=True,
        readonly=True,
    )

    motif_irreparabilite = fields.Selection(
        [
            ('oxidation_severe', 'Severe oxidation'),
            ('pieces_obsoletes', 'Obsolete parts'),
            ('cout_reparation', 'Repair cost > Device value'),
            ('autre', 'Other'),
        ],
        string='Irreparability Reason',
        required=True,
    )

    motif_irreparabilite_autre = fields.Text(
        string='Reason Details',
        help='Fill in this field if you selected "Other"',
    )

    def action_generate_certificate(self):
        """Generate the certificate and launch the PDF report"""
        self.ensure_one()

        if not self.repair_order_id.device_id:
            raise ValidationError(_(
                'The IMEI / Serial number is required to generate the irreparability certificate. '
                'Please fill it in on the repair order.'
            ))

        if self.motif_irreparabilite == 'autre' and not self.motif_irreparabilite_autre:
            raise ValidationError(_('Please fill in the reason details.'))

        # Save the data on the repair order
        self.repair_order_id.write({
            'motif_irreparabilite': self.motif_irreparabilite,
            'motif_irreparabilite_autre': self.motif_irreparabilite_autre,
            'date_certificat_irreparabilite': fields.Datetime.now(),
        })

        # Launch the PDF report
        return self.env.ref('uto_repair.action_report_irreparability_certificate').report_action(
            self.repair_order_id
        )
