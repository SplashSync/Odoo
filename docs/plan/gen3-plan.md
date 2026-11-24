# Odoo connector Gen 3 (splashpy 3.0) — analysis & plan, branch 20.0

> Internal name: **V3 / Gen 3** (Gen 2 may later carry older Odoo versions). GitLab milestones:
> `Odoo V3 · Foundations (20.0)`, `Odoo V3 · Objects (20.0)`, `Odoo V3 · Release (20.0)`, issues #3 → #31.

> Prepared 2026-11-23. Inputs: brief n°2 (Odoo V3), `Py-Core/docs/plan/odoo-v2-plan.md` and
> `Py-Core/docs/plan/odoo-v1-inventory.md` (V1 18.0 inventory), splashpy 3.0 (`Py-Core`, branch `3.0`),
> V1 manifest `docs/plan/v1-legacy-manifest.json`, `docs/plan/fields-v1-templates.md` (field ids → templates).
> Nothing is implemented yet. This file is the base for the GitLab milestones & work items.

## 0. Status (2026-11-24)

| Item | State |
|---|---|
| M1-01 cleanup | done: V1 addon, `resources/`, `setup.py`, old manifests removed (V1 manifest kept in `docs/plan/`) |
| M1-04 / M1-05 images | done: `docker/odoo/Dockerfile` (stages base, wheel, modules, init, odoo, db, dev); addon change = 24 s rebuild; stack ready in ~20 s |
| M1-06 compose & Makefile | done: one `docker/<image>.yml` per image, `make build up test quality reset update manifest` |
| M1-07 Toolkit | done: 3 SOAP connections (C0, PhpUnit1, PhpUnit2), local tests L01 / L02 copied (Order / Invoice, not run yet) |
| M1-08 CI | written (`.gitlab-ci.yml`, `ci/`), not run yet; no registry cache yet |
| M1-09 / M1-10 skeleton & config | done: controller on splashpy WSGI app, debug page, per-company settings on `res.company` (admin only), settings page |
| M1-13 generic fields | done: `_fields` discovery, groups per Odoo module, user access respected |
| M2-01 ThirdParty | done: templates, scope `ThirdParty.Provider`, phone on the MobilePhone template (single phone since Odoo 19), customer / supplier from Odoo ranks + read-only prospect; Toolkit green (840 tests) |
| M2-02 Address | done: templates, scope `Address.PostalAddress`, normalized types, microdata first / last fixed; Toolkit green (760 tests) |
| M2-03 / M2-04 / M2-06 Product | done: core (SKU, translated name & description, flags, barcode, dimensions), variants declared on the fly (no combination generated: Odoo `create_product_product=False` context, template lines cleaned from database state), attributes with translated values, gallery on `product.image` with per variant visible / cover flags (`splash_hidden_variant_ids`, `splash_cover_variant_ids`, depends on `website_sale`); scopes VariantsReceiver + GalleryReceiver; Toolkit green (884 tests) except a validator issue (see below). Prices / taxes, categories, stock & suppliers still to do |
| Translations | `<field>_<lang>` for translated fields (V1 ids), generic translatable fields included; HTML fields translated term by term; list columns `value_fr_FR@attributes` built in the addon (splashpy 3.0 produces `value@attributes_fr_FR`: to fix in Py-Core) |
| Validator issue | VariantsReceiver scenario: after deleting its first variant (step 3) the validator does not reload its objects list and may later read that deleted product → 1 to 3 random "unable to load" failures per run. Lists are newest first (with oldest first it picked the undeletable system products 1 & 2) |
| Generic groups | functional groups (General, Address, Accounting, E-Invoicing, Sales, Purchases, Stock, Website, Communication, Localization) |
| Robustness | every write in a savepoint (an Odoo refusal never aborts the request); `make test` runs one validator pass per object (the validator keeps ids of objects it deleted) |
| Quality | `make quality` green: ruff (strict rule set), pylint-odoo, ruff format, bandit, mypy strict |

## 1. Decisions taken

| Topic | Decision |
|---|---|
| Core | splashpy **3.0** (Py-Core branch `3.0`): fields groups with explicit order, templates & scopes, extensions, conformance suite, debug page |
| Branches | **one branch per Odoo version, nothing more**. Strategy: make `20.0` work well first, then go down step by step (`19.0`, then `18.0`), depending on how it goes |
| Code base | restart from scratch; V1 18.0 is the **functional reference** only |
| `resources/` | **removed** (submodule unregistered on `20.0`); everything it provided (docker, CI, make, toolkit tests) is rebuilt inside the branch |
| Tests | the **Toolkit 3.0 validator** is the reference test suite (+ local PHP tests for status transitions) |
| Docker | priority #1: images that build fast and restart in seconds, for local dev **and** CI/CD |
| Field ids | **V1 field ids are kept** (ex: `legal`, `first`, `client_order_ref`, `price_unit@lines`). Templates give type / microdata / names, never the id. Exceptions listed and validated case by case |
| Templates | every field with a matching template is built from it; checked with the Toolkit MCP. V1 microdata errors are fixed (`first` / `last` swapped) |
| Odoo fields | **all explicit fields are kept**, including the generic Odoo fields exposed by discovery, each in a dedicated group |
| Licence | base addon moves from GPL-3 to **LGPL-3** |
| Customer specific | `ons_*` fields stay available when their Odoo module is installed (extension enabled per database on module presence); "MY LED" fields move to a dedicated extension |
| Docker network | **one fixed network `172.120.0.0/24` for Odoo**, identical on every branch (one stack running locally at a time); addresses to agree, see §3.2 |

## 2. Analysis

### 2.1 What we start from

- V1 18.0: 87 Python files, 11 473 lines, 5 objects (ThirdParty, Address, Product, Order, Invoice),
  no Python tests, write order = alphabetical order of field ids, broken change detection
  (create commits never sent, no `account.move` commits, duplicates from stock moves), static caches
  shared between databases, `ws_key` readable by internal users. Details: Py-Core inventory.
- Docker V1: `odoo:${VERSION}` + Postgres + Toolkit, modules **installed at each boot**
  (`--init`), splashpy pip-installed at each boot, 3 companies created by a `post_init_hook`.
  → several minutes per start, this is what we replace.
- CI V1: pipeline included from the `resources` branch on GitHub, CI used splashpy from PyPI.
- Local Toolkit tests to keep: `L01OrderStatusTest.php`, `L02InvoicesStatusTest.php`
  (currently in `resources/docker/toolkit/tests`, to move in the branch).

### 2.2 Field ids & templates (first pass)

- Old manifest `splash.json`: 464 fields, of which ~310 auto-discovered from `fields_get()`
  (group "Others", `schema.org/Product/<label>` microdata, mostly noise: `message_*`, `activity_*`,
  `signup_*`, counters...).
- On the ~156 explicit V1 fields, **113 match a catalog template** on itemtype + itemprop.
  The others need a manual choice (MCP Toolkit) or stay custom.
- Found while matching:
  - `first` / `last` microdata are **swapped** in V1 (`first` = familyName, `last` = givenName).
    Templates will fix the microdata while keeping the ids → check impact on existing nodes.
  - `phone` vs `mobile`: ambiguous microdata (`ThirdParty.Core.Phone` / `MobilePhone`,
    `Address.Contact.Phone`); `res.partner.mobile` removed in Odoo 19+.
  - `splash.json` at the root is an old manifest (Odoo 12 names: `date_invoice`, `number`,
    `customer`, `supplier`, `__last_update`) → **the real 18.0 field list must be regenerated** from a
    running V1 18.0 before freezing the id table.
- Decision: all these fields are kept (ids unchanged), sorted in dedicated groups instead of one "Others" group.

### 2.3 Odoo 20 (image `odoo:20` = `20.0-20261112`, Python 3.12)

`odoo.osv` removed (`odoo.fields.Domain`), `_sql_constraints` → `models.Constraint`, no `name_get`,
products `type` + `is_storable`, mail tracking values removed. To check while coding:
`sale.order.line.tax_id`/`tax_ids`, `res.partner.mobile`, stock valuation, payment `memo`,
`sale.order` states, private methods used by V1 (`_create_variant_ids`, `_get_reconciled_payments`...).

### 2.4 Toolkit MCP

- `.mcp.json` points to `http://172.120.0.100/_mcp` (V1 stack, not running → unreachable).
- The new stack gives one Toolkit per branch with a fixed IP (see §3.2): the MCP is used to read the
  templates / scopes and to run the validator on single objects / fields while coding.
- Until then the catalog embedded in splashpy 3.0 was used offline for the first matching.

## 3. Target

### 3.1 Repository layout (branch `20.0`)

```
splashsync/            addon (base, LGPL-3), modules at the root (App Store)
docker/
    odoo/Dockerfile    ARG ODOO_VERSION: odoo + splashpy + pre-initialised filestore
    db/Dockerfile      postgres with a pre-initialised database (PGDATA=/pgdata)
    toolkit/           splash.yaml, phpunit.xml, tests/ (L01, L02...)
docker-compose.yml     db + odoo + toolkit (+ dev overrides)
Makefile               install, lint, style, stan, quality, build, up, test, stop, prune, manifest
.gitlab-ci.yml + ci/   Quality / Build / Functional
docs/                  getting started, configuration, objects, development
```

### 3.2 Docker: fast build, fast restart

1. **Base image per version** (`registry.gitlab.com/splashsync/odoo:20-base`): `odoo:20` + system
   deps + splashpy 3.0 wheel. Rebuilt only when Odoo or splashpy change.
2. **Pre-initialised database image**: at build, `odoo -i base,contacts,sale_management,stock,account,
   website_sale... --without-demo=all --stop-after-init` + test companies & config (replaces the V1
   `post_init_hook`). Postgres data under `PGDATA=/pgdata` (the official `VOLUME` would drop it);
   filestore embedded in the Odoo image, consistent with the database.
3. **Start = no install**: the container starts on the ready database (`-u splashsync` only when
   models / views / data changed, detected by a hash of the addon manifest + data files).
4. **Template database for tests**: `createdb -T odoo20_tpl test_<run>` (~1 s), each validator run
   on a fresh copy.
5. **Code mounted** in dev (`splashsync/` + optional local `Py-Core` with `pip install -e`),
   `--dev=reload,xml`; **code copied** in CI images.
6. **One network for Odoo**, the same on every branch: `172.120.0.0/24` (one stack at a time
   locally), plus the external `splashsync` network. Addresses to agree:
   Implemented with the V1 addresses (app `.10`, toolkit `.100`, db `.101`), so `.mcp.json` is
   unchanged (`http://172.120.0.100/_mcp`); still to confirm with the user (proposal: toolkit `.10`,
   app `.100`, db `.200`). Odoo and the Toolkit are also published on localhost (8069, 8080).
7. Healthchecks everywhere, `depends_on: service_healthy`, `make up` waits (`--wait`).
8. CI uses the same images (GitLab registry, BuildKit cache, tags per version + content hash).

### 3.3 Addon architecture (summary, details in Py-Core plan §2)

Thin controller → per-database `SplashClient` (no static state), config in `res.config.splash` /
`ir.config_parameter` (key not readable by internal users), contracts cache in database, objects as
fields groups with explicit order, fields from templates, scopes declared, commits batched per
transaction and sent after commit, extensions enabled per database (`splashsync_advanced`).

## 4. Milestones & work items

Ids `M<milestone>-<nn>` are local references until the GitLab work items exist.

### Milestone 1 — Foundations & environment (20.0)

Goal: `make up` gives in < 1 min a ready Odoo 20 + Toolkit 3.0 + MCP, CI green on an empty addon
that answers the Splash protocol.

| Id | Work item | Content | Done when |
|---|---|---|---|
| M1-01 | Branch 20.0 cleanup | `resources/` submodule removed, V1 addon, `venv/`, `mnt/`, `plugins/`, old manifests and `setup.py` removed; `.gitignore`, `.dockerignore`, README skeleton | branch contains only the Gen 3 layout |
| M1-02 | V1 18.0 reference manifest | run the V1 18.0 stack once, export `splash.json` / field lists per object (Toolkit `splash:server:manifest`), commit it under `docs/plan/` | real 18.0 field ids frozen as reference |
| M1-03 | Field ids ↔ templates table | finish `docs/plan/fields-v1-templates.md` with the MCP: template per field, custom fields, dropped fields, microdata fixes (`first`/`last`), validated with the user | table validated |
| M1-04 | Odoo image | `docker/odoo/Dockerfile` `ARG ODOO_VERSION`, splashpy 3.0 installed, entrypoint without install at boot, healthcheck | `docker build` cached < 30 s on code change |
| M1-05 | Pre-initialised database | `docker/db` image: modules, companies C0/C1/C2, users, langs, taxes, config, `PGDATA=/pgdata`, template db, matching filestore | Odoo up and healthy in < 15 s |
| M1-06 | Compose & Makefile | `docker-compose.yml` (db, odoo, toolkit), fixed network `172.120.0.0/24` (addresses agreed with the user), `make up / test / stop / prune / reset-db / update / manifest`, `.mcp.json` → toolkit | `make up && make test` work from scratch |
| M1-07 | Toolkit 3.0 configuration | `splash.yaml` (3 SOAP connections, one per company), `phpunit.xml` suites per object, local tests L01/L02 moved in, validator runs on a cloned db | validator runs (empty object list) |
| M1-08 | GitLab CI | stages Quality (ruff, mypy, pylint-odoo, oca hooks, bandit), Build (images to registry, cache), Functional (validator per object, junit reports, manifest artefacts) | pipeline green on `20.0` |
| M1-09 | Addon skeleton | manifest (real deps, version, licence), controller `/splash` on `client.handle_request()`, debug page, per-database client factory, error handling | Toolkit ping / connect OK |
| M1-10 | Configuration | `ConfigProvider` Odoo, settings view (General / Products / Sales), company resolution (`cid` / `cname`), access rights (key admin only) | settings saved, multi-company OK |
| M1-11 | Contracts cache in database | `CatalogCache` on the database, install / upgrade hook, optional cron | templates used offline, update works |
| M1-12 | Odoo helpers base | shared fields groups (audit dates, company, sales user / team), relations (m2o / m2m by id, name, Splash id), currency, taxes, translations — all per request, no static state | unit-tested helpers |
| M1-13 | Generic Odoo fields | discovery of the Odoo model fields from `_fields` (not `fields_get()`), V1 ids kept, sorted in dedicated groups, computed / technical noise read-only, per-object overrides as data | same generic ids as V1 18.0 reference |

### Milestone 2 — Objects (20.0)

Each object: fields groups with explicit order / phases, **V1 ids kept**, fields from templates,
scopes declared, Toolkit validator green (CRUD, lists, fields, scopes) on the 3 companies.

| Id | Work item | Content | Done when |
|---|---|---|---|
| M2-01 | ThirdParty | `res.partner` companies / persons: names (`legal`, `first`, `last` encoding), contact, country / state, flags, VAT, scope `ThirdParty.Provider` | validator ThirdParty green |
| M2-02 | Address | child partners, required `parent_id`, contact-type rules, postal address, scope `Address.PostalAddress` | validator Address green |
| M2-03 | Product core & prices | template / variant resolution (create phase), SKU detection, core, flags, dimensions, prices & taxes (explicit order), currency, categories / brand relations | validator Product (simple products) green |
| M2-04 | Product attributes & variants | attributes, values, PTAV, variants list, features (`__feature_id__*`), scope `Product.VariantsProvider` | validator variants green |
| M2-05 | Product stock & suppliers | `is_storable`, `qty_available` through quants, per-warehouse free qty, supplier info as one group | validator stock fields green |
| M2-06 | Product images | gallery from `image_1920`, variants, `product.image`, files served to Splash, scope `Product.GalleryProvider` | validator images green |
| M2-07 | Order | header, partners, lines (product detection, taxes, priority), carrier, shipping address RO, status after lines, delivery after status, self-invoiced mode, scope `Order.Erp` | validator Order + L01 green |
| M2-08 | Invoice | header, lines (draft), status (post phase), payments (after status, comparison fixed), amounts check | validator Invoice + L02 green |
| M2-09 | Change detection | ORM hooks on partners, products / templates, stock, orders, account moves; commits on created records, relevant fields only, deduplicated per transaction, sent after commit, none while Splash writes | commits checked with `expect_commit()` / Toolkit |
| M2-10 | Generated manifests | `make manifest` → `splash.json` / `splash.yml` / `swagger.json` committed; diff of field ids vs M1-02 reference = only the validated changes | id diff reviewed |

### Milestone 3 — Release (20.0)

| Id | Work item | Content | Done when |
|---|---|---|---|
| M3-01 | Hardening | MCP Splash end-to-end on a dedicated test node, performance of lists / large catalogs, logs, error messages | E2E sync OK on a real node |
| M3-02 | Documentation | README, install / configuration guide, field reference generated from the manifest | docs published |
| M3-03 | App Store packaging 20.0 | manifest, description page, icons, screenshots, licence LGPL-3 | module accepted on the App Store |
| M3-04 | Lower versions | once 20.0 works well: port to `19.0`, then `18.0`, one branch each, depending on results | — |
| M3-05 | `splashsync_advanced` | private repo, OPL-1, extensions enabled per database; content to decide | first paid feature delivered |
| M3-06 | Customer extensions | "MY LED" fields in a dedicated extension; `ons_*` fields enabled when their module is installed | fields only exposed where relevant |
| M3-07 | V1 freeze & cleanup | V1 branches frozen, `master` / `multi_versions` / `detached` / old WIP branches cleaned, issues #1 / #2 closed or moved, old milestone closed | repo clean |

## 5. Answers (2026-11-23)

1. Generic Odoo fields: kept, ids unchanged, in dedicated groups.
2. `first` / `last` microdata: fixed with templates, ids unchanged.
3. Licence: LGPL-3.
4. Branches: one per version, `20.0` only for now.
5. Customer fields: `ons_*` kept when their module is installed, "MY LED" in a dedicated extension.
6. Network: single `172.120.0.0/24`, homogeneous across branches; addresses to agree together.
7. Milestones & work items: created in GitLab `SplashSync/Odoo`.
