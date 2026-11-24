[![N|Solid](https://github.com/SplashSync/Php-Core/raw/master/img/github.jpg)](https://www.splashsync.com)

# Splash Sync Connector for Odoo 20 (Gen 3)

Odoo addon `splashsync`: synchronize Odoo with any application through [Splash Sync](https://www.splashsync.com).
Gen 3 is built on **splashpy 3.0** ([Py-Core](https://gitlab.com/SplashSync/Py-Core), branch `3.0`).
One branch per Odoo version: this is `20.0`.

## Status

| Object      | Odoo model    | State                                                          |
|-------------|---------------|----------------------------------------------------------------|
| ThirdParty  | `res.partner` | Done: templates, scope `ThirdParty.Provider`, Toolkit green    |
| Address     | `res.partner` | Done: templates, scope `Address.PostalAddress`, Toolkit green  |
| Product     | `product.product` | Core, translations, variants & gallery: scopes `VariantsReceiver`, `GalleryReceiver`; prices, stock & suppliers planned |
| Order       | `sale.order`  | Planned                                                        |
| Invoice     | `account.move`| Planned                                                        |

Field ids of the V1 connector are kept. Plan & field correspondence: `docs/plan/`.

## Requirements

* Odoo 20, Python 3.12
* splashpy 3.0
* An active Splash Sync account

## Development

Everything runs in Docker. Images are built once and pushed to the registry of the project
(`registry.gitlab.com/splashsync/odoo/odoo|db|dev:20`): Odoo with its modules, the pre-initialised
database, the quality tools. The addon and splashpy (`SPLASHPY_PATH`) are mounted from the sources:
a code change never needs a rebuild.

```bash
docker network create splashsync --attachable   # once
make pull       # images of the branch from the registry (or: make build)
make up         # start Odoo, database, Adminer & Toolkit (ready in seconds)
make quality    # ruff, pylint-odoo, format, bandit, mypy strict (in the dev image)
make test       # Toolkit 3.0 validator, one run per object, on the 3 test companies
make reset      # back to the database of the image
make build push # only when docker/odoo changes (CI does it on the version branch)
```

CI: `Build` builds & pushes the images only when `docker/odoo` changes, on schedules or with
`BUILD_IMAGES=1`; `Quality` runs in the dev image, `Functional` pulls the images, upgrades the addon
of the commit at start (`ODOO_UPDATE=1`) and runs the validator. Nothing is rebuilt on a code push.

| Service | URL                                           | Notes                                  |
|---------|-----------------------------------------------|----------------------------------------|
| Odoo    | http://localhost:8069                         | test login `admin` / `admin`           |
| Splash  | http://localhost:8069/splash?node=ThisIsOdooC0WsId | debug page of the main company   |
| Toolkit | http://localhost:8080                         | MCP: `http://172.120.0.100/_mcp`       |
| Adminer | http://localhost:8081                         | Postgres admin: server `db.odoo.local`, `odoo` / `odoo` |

splashpy is built from a local Py-Core checkout (`SPLASHPY_PATH`, default `../../../SplTools/Py-Core`
relative to `docker/`). Network: `172.120.0.0/24`, the same on every branch (one stack at a time).

## License

LGPL-3. This module is part of the [Splash Sync](https://www.splashsync.com) project.
