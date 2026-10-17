# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RepairIrrepailibilityCertificateWizard(models.TransientModel):
    _name = 'repair.irreparability.certificate.wizard'
    _description = 'Wizard pour générer le certificat d\'irréparabilité'

    repair_order_id = fields.Many2one(
        'repair.order',
        string='Fiche de réparation',
        required=True,
        readonly=True,
    )

    motif_irreparabilite = fields.Selection(
        [
            ('oxidation_severe', 'Oxydation sévère'),
            ('pieces_obsoletes', 'Pièces obsolètes'),
            ('cout_reparation', 'Coût de réparation > Valeur appareil'),
            ('autre', 'Autre'),
        ],
        string='Motif de l\'irréparabilité',
        required=True,
    )

    motif_irreparabilite_autre = fields.Text(
        string='Précisions sur le motif',
        help='Remplissez ce champ si vous avez sélectionné "Autre"',
    )

    def action_generate_certificate(self):
        """Génère le certificat et lance le rapport PDF"""
        self.ensure_one()

        if not self.repair_order_id.device_id:
            raise ValidationError(_(
                'Le numéro IMEI / Série est obligatoire pour générer le certificat d\'irréparabilité. '
                'Veuillez le renseigner dans la fiche de réparation.'
            ))

        if self.motif_irreparabilite == 'autre' and not self.motif_irreparabilite_autre:
            raise ValidationError(_('Veuillez remplir les précisions sur le motif.'))

        # Enregistre les données sur la fiche de réparation
        self.repair_order_id.write({
            'motif_irreparabilite': self.motif_irreparabilite,
            'motif_irreparabilite_autre': self.motif_irreparabilite_autre,
            'date_certificat_irreparabilite': fields.Datetime.now(),
        })

        # Lance le rapport PDF
        return self.env.ref('uto_repair.action_report_irreparability_certificate').report_action(
            self.repair_order_id
        )
