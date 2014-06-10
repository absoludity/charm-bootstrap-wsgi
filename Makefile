#!/usr/bin/make
PYTHON := /usr/bin/env python

build: sync-charm-helpers test

lint:
	@flake8 --exclude hooks/charmhelpers --ignore=E125 hooks
	@flake8 --exclude hooks/charmhelpers --ignore=E125 unit_tests
	@charm proof

test:
	@echo Starting tests...
	@PYTHONPATH=./hooks $(PYTHON) /usr/bin/nosetests --nologcapture unit_tests

/tmp/charm_helpers_sync.py:
	@bzr cat lp:charm-helpers/tools/charm_helpers_sync/charm_helpers_sync.py \
		> /tmp/charm_helpers_sync.py

sync-charm-helpers: /tmp/charm_helpers_sync.py
	@$(PYTHON) /tmp/charm_helpers_sync.py -c charm-helpers.yaml

/tmp/charm-ansible-roles:
	@git clone https://github.com/absoludity/charm-ansible-roles.git /tmp/charm-ansible-roles

sync-ansible-roles: /tmp/charm-ansible-roles /tmp/canonical-ansible-roles
	@echo "Removing and re-creating reusable roles from sources..."
	@rm -rf roles/*
	@cd /tmp/charm-ansible-roles && git pull
	@cp -a /tmp/charm-ansible-roles/wsgi-app ./roles

deploy:
	@echo Deploying charm-bootstrap-wsgi as wsgi-example with gunicorn.
	@juju deploy --num-units 2 --repository=../.. local:precise/charm-bootstrap-wsgi wsgi-example
	@juju set wsgi-example build_label=r1
	@juju deploy gunicorn
	@juju add-relation wsgi-example gunicorn
	@echo See the README for explorations after deploying.

curl:
	juju run --service wsgi-example "curl -s http://localhost:8080"
