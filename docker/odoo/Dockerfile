################################################################################
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#
################################################################################

# Splash Odoo connector (Gen 3) - ready to use images, nothing installed at start.
#
#   base    official Odoo image, configuration, "packaging" (versioned external dependencies)
#   modules builds the database once with the Odoo modules (cached)
#   init    installs the addon and the test fixtures (companies, Splash configuration)
#   odoo    Odoo + addon + filestore matching the "db" image
#   db      Postgres with the pre-initialised database (PGDATA outside the official VOLUME)
#   dev     "odoo" + quality tools (ruff, mypy, pylint-odoo), run against the installed addon
#
# Build: make build (only when this directory changes), then make push. Day to day, images come
# from the registry (make pull): the addon sources are mounted, nothing is rebuilt.
# splashpy comes from PyPI (SPLASHPY, a pip requirement): "splashpy>=3.0.0b0,<4" takes the latest 3.x
# release, betas included (a pre-release in the specifier lets pip pick pre-releases), never 4.x.

ARG ODOO_VERSION=20
ARG POSTGRES_VERSION=17
ARG SPLASHPY="splashpy>=3.0.0b0,<4"

################################################################################
# Base: official Odoo image, addons & data outside its VOLUMEs (they stay in the image)
FROM odoo:${ODOO_VERSION} AS base

USER root
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    SPLASH_ADDONS=/opt/splash/addons \
    SPLASH_DATA=/var/lib/odoo-data

# Odoo needs "packaging" to check versioned external dependencies ("splashpy>=3.0.0b0,<4")
RUN mkdir -p ${SPLASH_ADDONS} ${SPLASH_DATA} && chown -R odoo:odoo ${SPLASH_DATA} \
    && pip3 install packaging
COPY docker/odoo/odoo.conf /etc/odoo/odoo.conf

################################################################################
# Modules: database with the Odoo modules (cached until the modules list changes)
FROM base AS modules

ARG POSTGRES_VERSION
ARG ODOO_MODULES=contacts,product,sale_management,stock,sale_stock,purchase,account,delivery,website_sale,l10n_fr_account,l10n_fr_payment
ENV PGDATA=/pgdata \
    PG_BIN=/usr/lib/postgresql/${POSTGRES_VERSION}/bin

RUN echo "deb http://apt.postgresql.org/pub/repos/apt noble-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-${POSTGRES_VERSION} \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p ${PGDATA} /var/run/postgresql && chown postgres:postgres ${PGDATA} /var/run/postgresql \
    && su postgres -c "${PG_BIN}/initdb -D ${PGDATA} -U odoo --auth-local=trust --auth-host=scram-sha-256 -E UTF8 --locale=C.UTF-8" \
    && echo "listen_addresses = '*'" >> ${PGDATA}/postgresql.conf \
    && echo "host all all all scram-sha-256" >> ${PGDATA}/pg_hba.conf

COPY docker/odoo/pg.sh /usr/local/bin/pg.sh

RUN pg.sh start \
    && pg.sh exec "psql -U odoo -d postgres -c \"ALTER USER odoo PASSWORD 'odoo'\"" \
    && su odoo -s /bin/bash -c "odoo -c /etc/odoo/odoo.conf --db_host=/var/run/postgresql -d odoo \
        -i base,${ODOO_MODULES} --load-language=fr_FR --stop-after-init --log-level=warn" \
    && pg.sh stop

################################################################################
# Init: Splash addon & test fixtures (rebuilt when the addon changes)
FROM modules AS init

ARG SPLASHPY
RUN pip3 install "${SPLASHPY}"
COPY --chown=odoo:odoo splashsync ${SPLASH_ADDONS}/splashsync
COPY docker/odoo/fixtures.py /opt/splash/fixtures.py
RUN pg.sh start \
    && su odoo -s /bin/bash -c "odoo -c /etc/odoo/odoo.conf --db_host=/var/run/postgresql -d odoo \
        -i splashsync --stop-after-init --log-level=warn" \
    && su odoo -s /bin/bash -c "odoo shell -c /etc/odoo/odoo.conf --db_host=/var/run/postgresql -d odoo \
        --log-level=warn --shell-interface=python < /opt/splash/fixtures.py" \
    && pg.sh stop

################################################################################
# Odoo: addon + filestore matching the database
FROM base AS odoo

ARG SPLASHPY
RUN pip3 install "${SPLASHPY}"
COPY --from=init --chown=odoo:odoo ${SPLASH_DATA} ${SPLASH_DATA}
COPY --chown=odoo:odoo splashsync ${SPLASH_ADDONS}/splashsync
COPY docker/odoo/entrypoint.sh /usr/local/bin/splash-entrypoint.sh

USER odoo
EXPOSE 80
HEALTHCHECK --interval=2s --timeout=3s --retries=60 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1/web/health')"
ENTRYPOINT ["/usr/local/bin/splash-entrypoint.sh"]
CMD ["odoo"]

################################################################################
# Database: the pre-initialised cluster
FROM postgres:${POSTGRES_VERSION} AS db

ENV PGDATA=/pgdata
COPY --from=init --chown=postgres:postgres /pgdata /pgdata
HEALTHCHECK --interval=1s --timeout=2s --retries=30 CMD pg_isready -U odoo -d odoo

################################################################################
# Dev: quality tools against the installed addon (same Odoo, same Python)
FROM odoo AS dev

USER root
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/* \
    && pip3 install ruff mypy pylint-odoo bandit
USER odoo
WORKDIR /opt/splash
