# Guide de Création et Téléchargement de Factures

## Accès au Système

1. Connectez-vous à l'interface d'administration : **https://api2.bellehouseniger.com/admin/**
2. Entrez vos identifiants administrateur

---

## Créer une Facture

### Étape 1 : Accéder aux Factures
- Dans le menu de gauche, cliquez sur **"Facturation"** → **"Factures"**
- Cliquez sur le bouton **"Ajouter Facture"** en haut à droite

### Étape 2 : Remplir les Informations
Remplissez les champs suivants :

- **Projet** : Sélectionnez le projet concerné
- **Date d'émission** : Date de création de la facture
- **Date d'échéance** : Date limite de paiement
- **Objet** : Description brève (ex: "Travaux de fondation")
- **Statut** : Brouillon / En attente / Payée / Annulée
- **Type de taxe** : Choisir le type de TVA applicable
- **Pourcentage de taxe** : Taux de TVA (ex: 19%)
- **Acompte versé** : Montant déjà payé (optionnel)
- **Notes** : Informations supplémentaires (optionnel)

### Étape 3 : Ajouter les Articles
En bas de la page, dans la section **"Articles de facture"** :

1. Cliquez sur **"Ajouter un autre Article de facture"**
2. Pour chaque article, renseignez :
   - **Désignation** : Description de l'article (ex: "Fondation")
   - **Quantité** : Nombre d'unités
   - **Prix unitaire HT** : Prix par unité (FCFA)
   - **Ordre** : Position dans la liste (1, 2, 3...)

3. Répétez pour chaque article

### Étape 4 : Enregistrer
- Cliquez sur **"Enregistrer"** en bas de la page
- Le numéro de facture sera généré automatiquement

---

## Télécharger la Facture en PDF

### Méthode 1 : Depuis la Liste des Factures
1. Allez dans **"Facturation"** → **"Factures"**
2. Trouvez la facture souhaitée
3. Cliquez sur le numéro de la facture pour l'ouvrir
4. En haut de la page, cliquez sur **"Download PDF"**
5. Le fichier PDF se télécharge automatiquement

### Méthode 2 : Depuis l'API (pour développeurs)
```
GET /api/admin/invoices/{id}/download-pdf/
```

---

## Calculs Automatiques

Le système calcule automatiquement :
- ✅ **Montant Total HT** : Somme de tous les articles
- ✅ **Taxe** : Montant Total HT × Pourcentage de taxe
- ✅ **Montant Total TTC** : Total HT + Taxe
- ✅ **Net à Payer** : Total TTC - Acompte versé

---

## Statuts des Factures

| Statut | Description |
|--------|-------------|
| **Brouillon** | Facture en préparation, non envoyée |
| **En attente** | Facture envoyée, en attente de paiement |
| **Payée** | Paiement reçu |
| **Annulée** | Facture annulée |

---

## Conseils

- 📋 Vérifiez toujours les montants avant de télécharger
- 💾 Le PDF inclut automatiquement le logo Belle House
- 📧 Vous pouvez envoyer le PDF directement au client par email
- ✏️ Les factures peuvent être modifiées tant qu'elles sont en statut "Brouillon"

---

## Support

Pour toute assistance, contactez l'administrateur système.
