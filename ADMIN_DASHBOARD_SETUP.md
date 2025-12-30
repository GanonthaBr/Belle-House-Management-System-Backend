# Belle House - Guide d'Installation du Nouveau Tableau de Bord Admin

## 🎨 Nouveau Design Moderne

Votre tableau de bord administratif a été entièrement modernisé avec :
- ✨ Interface moderne et responsive
- 🇫🇷 Français par défaut avec option anglais
- 🎯 Navigation intuitive
- 📊 Tableaux de bord interactifs
- 🎨 Design personnalisé Belle House

## Installation

### 1. Installer les nouvelles dépendances

```powershell
# Installer django-jazzmin
pip install django-jazzmin

# Ou réinstaller toutes les dépendances
pip install -r requirements.txt
```

### 2. Collecter les fichiers statiques

```powershell
python manage.py collectstatic --noinput
```

### 3. Créer les fichiers de traduction (optionnel)

```powershell
# Créer les fichiers de traduction français
python manage.py makemessages -l fr

# Créer les fichiers de traduction anglais
python manage.py makemessages -l en

# Compiler les traductions
python manage.py compilemessages
```

### 4. Redémarrer le serveur

```powershell
python manage.py runserver
```

## 🌐 Accès au Nouveau Tableau de Bord

Visitez : `http://localhost:8000/admin/`

## 🎨 Personnalisation

### Couleurs du Thème Belle House

Les couleurs personnalisées sont définies dans `staticfiles/admin/css/custom_admin.css` :

- **Primaire**: `#2c3e50` (Bleu foncé)
- **Secondaire**: `#e67e22` (Orange Belle House)
- **Accent**: `#3498db` (Bleu clair)
- **Succès**: `#27ae60` (Vert)
- **Avertissement**: `#f39c12` (Orange)
- **Danger**: `#e74c3c` (Rouge)

### Modifier le Logo

1. Ajoutez votre logo dans `media/` ou `staticfiles/`
2. Dans `config/settings.py`, modifiez :

```python
JAZZMIN_SETTINGS = {
    "site_logo": "chemin/vers/votre/logo.png",  # Ajoutez le chemin
    "login_logo": "chemin/vers/votre/logo.png",
    ...
}
```

### Personnaliser les Icônes

Dans `config/settings.py`, section `JAZZMIN_SETTINGS["icons"]`, vous pouvez modifier les icônes de chaque modèle.

Icônes disponibles : [Font Awesome Icons](https://fontawesome.com/icons)

### Changer le Thème de Couleur

Dans `config/settings.py`, section `JAZZMIN_UI_TWEAKS` :

```python
JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",  # Options: flatly, darkly, cosmo, cerulean, etc.
    "navbar": "navbar-dark navbar-primary",  # Barre de navigation
    "sidebar": "sidebar-dark-primary",  # Barre latérale
    ...
}
```

Thèmes disponibles : flatly, darkly, cosmo, cerulean, cyborg, journal, litera, lumen, lux, materia, minty, pulse, sandstone, simplex, sketchy, slate, solar, spacelab, superhero, united, yeti

## 🌍 Changement de Langue

### Pour les Utilisateurs

1. Connectez-vous au tableau de bord admin
2. En haut à droite, cliquez sur le menu de langue
3. Sélectionnez "Français" ou "English"

### Configuration par Défaut

Dans `config/settings.py` :

```python
LANGUAGE_CODE = 'fr'  # 'fr' pour français, 'en' pour anglais
```

## 📱 Fonctionnalités

### Navigation Latérale

Applications organisées par catégorie :
- 👥 **Clients** : Clients, Projets, Mises à jour, Promotions
- 🏗️ **Prospects** : Leads de construction, Demandes de contact
- 📢 **Marketing** : Services, Portfolio, Témoignages, Partenaires, Blog
- 💰 **Facturation** : Factures, Paiements
- 🔔 **Notifications** : Système de notifications

### Tableau de Bord

- Vue d'ensemble des statistiques
- Accès rapide aux actions courantes
- Recherche globale
- Filtres avancés

### Formulaires

- Onglets horizontaux pour une meilleure organisation
- Validation en temps réel
- Interface moderne et intuitive

## 🔧 Dépannage

### Les styles ne s'appliquent pas

```powershell
python manage.py collectstatic --clear --noinput
```

### Erreur "jazzmin not found"

```powershell
pip install django-jazzmin
```

### Les traductions ne s'affichent pas

```powershell
python manage.py compilemessages
```

## 📚 Ressources

- [Documentation Jazzmin](https://django-jazzmin.readthedocs.io/)
- [Django Admin](https://docs.djangoproject.com/fr/4.2/ref/contrib/admin/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [Bootstrap Themes](https://bootswatch.com/)

## 🎯 Prochaines Étapes

1. **Ajoutez votre logo** : Placez votre logo dans le dossier media et mettez à jour settings.py
2. **Personnalisez les couleurs** : Modifiez `custom_admin.css` selon votre charte graphique
3. **Traduisez l'interface** : Complétez les fichiers de traduction dans `locale/`
4. **Configurez les permissions** : Définissez les rôles et permissions utilisateurs

## 💡 Conseils

- Utilisez le **UI Builder** (bouton en bas de la sidebar) pour tester différents thèmes en temps réel
- Les changements de configuration nécessitent un redémarrage du serveur
- Testez toujours en mode DEBUG avant de déployer en production

---

**Besoin d'aide ?** Consultez la documentation ou contactez l'équipe technique Belle House.
