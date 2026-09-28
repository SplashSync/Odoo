---
lang: fr
permalink: start/composer
title: Installation
description: Installer le package Splash Core depuis PyPi et le module Splash pour Odoo.
updated: 2026-09-28
translation:
    from:        en
    source_hash: 7a06d89d
    mode:        llm
---

### Installer le package Splash Core depuis PyPi

Le module Odoo nécessite l'installation de notre package de base pour Python.

Vous pouvez l'installer via cette commande :

```bash
pip3 install splashpy
```

### Installer le module Splash pour Odoo

Téléchargez le module Splash pour Odoo depuis notre dépôt GitHub, et créez un lien symbolique dans le dossier des addons d'Odoo.

```bash
git clone https://github.com/SplashSync/Odoo.git /home/splashsync --depth=1
ln -s /home/splashsync/odoo/addons/splashsync /mnt/extra-addons
```

Pour mettre à jour le module, il vous suffit de mettre à jour le dépôt Git.

```bash
cd /home/splashsync && git pull
```

### Installation | Mise à jour automatisée

Si vous travaillez sur un environnement Ubuntu/Debian et que vos modules Odoo sont installés dans `/mnt/extra-addons/`, vous pouvez tester la commande suivante :

```bash
curl -s https://raw.githubusercontent.com/SplashSync/Odoo/master/scripts/install.sh | bash
```

> [!NOTE]
> Nécessite des droits administrateur.
