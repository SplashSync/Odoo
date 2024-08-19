[![N|Solid](https://github.com/SplashSync/Php-Core/raw/master/img/github.jpg)](https://www.splashsync.com)

# Splash Sync - Common Submodule for Odoo
Collector Branch for All Common parts of our Odoo Modules

Just used for DEV

## Contributing

Any Pull requests are welcome! 

This module is part of [SplashSync](http://www.splashsync.com) project.

## How to debug Odoo from PyCharm

### Create a DEV Container

PyCharm fail while using an include in docker files, thus we need a dev container


### Create Interpreter

Select Docker Compose, setup docker-compose.yaml path and select dev container

### Configure Run Configuration
- Python runner
- With Docker Interpreter
- Script ==> /usr/bin/odoo
- Path Mapping => See Screenshots
