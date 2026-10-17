# Implémentation : Certificat d'Irréparabilité

## ✅ Tâche Complétée

Implémentation complète du système de génération de certificat d'irréparabilité pour les appareils marqués comme "Mort" (Non réparable).

---

## 📝 Fichiers Créés

### 1. **Modèle de Données** 
- Fichier : `utopya/utopya-optline/uto_repair/models/repair.py`
- Modifications :
  - Ajout de 3 nouveaux champs sur `repair.order` :
    - `motif_irreparabilite` : Sélection du motif (Oxydation sévère, Pièces obsolètes, Coût > Valeur, Autre)
    - `motif_irreparabilite_autre` : Texte libre pour préciser si "Autre" est sélectionné
    - `date_certificat_irreparabilite` : Date/heure de génération du certificat
  - Ajout de la méthode `action_open_irreparability_wizard()` pour ouvrir le wizard

### 2. **Wizard de Saisie du Motif**
- Fichier : `wizard/irreparability_certificate.py` (créé)
- Fichier : `wizard/irreparability_certificate_views.xml` (créé)
- Fonctionnalités :
  - Formulaire modal pour saisir le motif d'irréparabilité
  - Validation pour le motif "Autre"
  - Enregistrement des données sur la fiche de réparation
  - Lancement automatique du rapport PDF après confirmation

### 3. **Rapport PDF / QWeb**
- Fichier : `views/report_irreparability_certificate.xml` (créé)
- Contenu du certificat :
  - En-tête avec logo et informations de la société
  - Infos sur l'appareil (type, marque, modèle, numéro de série/IMEI)
  - Infos du client (nom, adresse, téléphone)
  - Résultat du diagnostic avec motif d'irréparabilité
  - Clause légale pour les assurances
  - Espace pour signature et tampon

### 4. **Interface Utilisateur**
- Fichier : `views/repair_views.xml`
- Ajouts :
  - Bouton "Générer Certificat Irréparabilité" dans l'en-tête du formulaire
  - Groupe de champs affichant le motif et la date du certificat (caché si non généré)
  - Visibilité du bouton : apparaît uniquement quand la réparation est marquée comme "Faite"

### 5. **Déclarations & Configuration**
- Fichier : `__manifest__.py` - Ajout des 2 nouveaux fichiers XML
- Fichier : `wizard/__init__.py` - Import du nouveau wizard
- Fichier : `security/ir.model.access.csv` - Droits d'accès pour le wizard

---

## 🎯 Fonctionnalités Implémentées

### Action 1 : Déclencheur UI ✅
- Bouton "Générer Certificat Irréparabilité" dans la fiche de réparation
- Pop-up (wizard) demandant le motif de l'irréparabilité
- Options prédéfinies + texte libre si "Autre"

### Action 2 : Facturation du Diagnostic ✅
- **Indépendant** de la génération du certificat
- Le technicien peut ajouter une ligne "Forfait Diagnostic" sans restriction
- L'encaissement en caisse fonctionne normalement
- ✅ Aucun blocage

### Action 3 : Modèle PDF / QWeb ✅
- Template complet avec tous les éléments demandés :
  - Logo du magasin
  - Nom et adresse complète
  - Téléphone et email
  - SIRET
  - Numéro du ticket
  - Infos technicien
  - Infos appareil
  - Infos client
  - Résultat diagnostic avec motif
  - Clause légale
  - Espace signature/tampon

---

## 🔄 Workflow d'Utilisation

1. **Fiche de réparation ouverte**
   - L'appareil est marqué comme "Faite" (`is_ro_repaired = True`)
   - Le bouton "Générer Certificat Irréparabilité" devient visible

2. **Clic sur le bouton**
   - Un wizard (pop-up) s'ouvre
   - Saisie du motif d'irréparabilité
   - Si "Autre" : saisie de précisions

3. **Confirmation**
   - Les données sont enregistrées sur la fiche
   - Le rapport PDF est généré et téléchargé
   - Le certificat s'affiche dans un groupe caché (visible après génération)

4. **Facturation indépendante**
   - Le technicien peut ajouter des lignes "Forfait Diagnostic"
   - Création et encaissement de la facture normalement

---

## ✅ Validation

Module rechargé avec succès :
```
2026-04-26 16:52:58,980 INFO uto_ce_2812 loading uto_repair/views/report_irreparability_certificate.xml ✓
2026-04-26 16:52:58,998 INFO uto_ce_2812 loading uto_repair/wizard/irreparability_certificate_views.xml ✓
2026-04-26 16:52:59,010 INFO uto_ce_2812 Module uto_repair loaded successfully ✓
```

Pas d'erreurs de déploiement.

---

## 📊 Ressources Créées

- 1 modèle TransientModel (wizard)
- 1 rapport QWeb-PDF
- 3 champs sur repair.order
- 1 méthode d'action
- 2 fichiers XML de configuration
- 1 entrée CSV d'accès
