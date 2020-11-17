---
lang: en
permalink: start/composer
title: Install
---

### Install Splash Core Package from PyPi

Odoo Module require installation of our foundation package for Python.

You can install it with this command: 

```bash
pip3 install splashpy
```

### Install Splash Addon for Odoo

Download {{ site.github.project_title }} from our GitHub repository, and create a symlink to your Odoo addons path.

```bash
git clone https://github.com/SplashSync/Odoo.git /home/splashsync --depth=1
ln -s /home/splashsync/odoo/addons/splashsync /mnt/extra-addons
```

To update our module to it's last version, just pull sources.

```bash
cd /home/splashsync && git pull
```

### Automated Installation | Upgrade 

If you are working on an Ubuntu/Debian environment and have Odoo addons installed in ***/mnt/extra-addons/***.

You should try this command:

```bash
curl -s  https://raw.githubusercontent.com/SplashSync/Odoo/master/scripts/install.sh | bash
```

**Note**: Require admin rights
