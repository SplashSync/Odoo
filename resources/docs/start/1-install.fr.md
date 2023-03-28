---
lang: fr
permalink: start/composer
title: Installation
---

### Installer le Package Splash Core depuis PyPi

Odoo Module nécessite l'installation de notre module de base pour Python.

Vous pouvez l'installer via cette commande:

```bash
pip3 install splashpy
```

### Installer le module Splash pour Odoo

Téléchargez {{ site.github.project_title }} depuis notre dépôt GitHub, et créez un lien symbolique dans le dossier extra-addons de Odoo.

```bash
git clone https://github.com/SplashSync/Odoo.git /home/splashsync --depth=1
ln -s /home/splashsync/odoo/addons/splashsync /mnt/extra-addons
```

Pour mettre à jour le module, il vous suffit de mettre à jour le dépôt Git.

```bash
cd /home/splashsync && git pull
```

### Installation | Mise à jour automatisée 

Si vous travaillez sur un environnement Ubuntu/Debian et que vos modules Odoo sont installés dans ***/mnt/extra-addons/***.
Ou si vous utilisez une image docker.

Vous pouvez tester la ligne de commande suivante: 

```bash
curl -s  https://raw.githubusercontent.com/SplashSync/Odoo/master/scripts/install.sh | bash
```

**Note**: Nécéssite des droits administrateur