---
lang: en
permalink: start/composer
title: Install
description: Install the Splash core package from PyPi and the Splash addon for Odoo.
updated: 2026-09-28
---

### Install Splash Core Package from PyPi

The Odoo module requires our foundation package for Python.

You can install it with this command:

```bash
pip3 install splashpy
```

### Install Splash Addon for Odoo

Download the Splash module for Odoo from our GitHub repository, and create a symlink to your Odoo addons path.

```bash
git clone https://github.com/SplashSync/Odoo.git /home/splashsync --depth=1
ln -s /home/splashsync/odoo/addons/splashsync /mnt/extra-addons
```

To update our module to its latest version, just pull sources.

```bash
cd /home/splashsync && git pull
```

### Automated Installation | Upgrade

If you are working on an Ubuntu/Debian environment and have Odoo addons installed in `/mnt/extra-addons/`, you should try this command:

```bash
curl -s https://raw.githubusercontent.com/SplashSync/Odoo/master/scripts/install.sh | bash
```

> [!NOTE]
> Requires admin rights.
