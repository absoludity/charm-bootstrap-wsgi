#!/usr/bin/make
PYTHON := /usr/bin/env python
REVIEWS_CODE = ../.sourcecode/rnr-server/
REVIEWS_REVNO = 249

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
	@cp -a /tmp/charm-ansible-roles/nrpe-external-master ./roles

deploy: create-tarball
	@echo Deploying ubuntu-reviews r$(REVIEWS_REVNO) with gunicorn.
	@juju deploy --num-units 2 --repository=../.. local:precise/ubuntu-reviews
	@juju set ubuntu-reviews build_label=r$(REVIEWS_REVNO)
	@juju deploy gunicorn
	@juju deploy nrpe-external-master
	@juju add-relation ubuntu-reviews gunicorn
	@juju add-relation ubuntu-reviews nrpe-external-master
	@echo See the README for explorations after deploying.

curl:
	juju run --service ubuntu-reviews "curl -s http://localhost:8080"

nagios:
	juju run --service ubuntu-reviews "egrep -oh /usr.*lib.* /etc/nagios/nrpe.d/check_* | sudo -u nagios -s bash"

collect-code: $(REVIEWS_CODE)

$(REVIEWS_CODE):
	@echo Grabbing the reviews server code
	@mkdir -p ../.sourcecode
	@cd ../.sourcecode && bzr branch -r $(REVIEWS_REVNO) lp:rnr-server
	@echo "Pulling required branhc dependencies (this requires python-fabric)"
	@cd ../.sourcecode/rnr-server && fab pull_required_branches

create-tarball: $(REVIEWS_CODE) files/r$(REVIEWS_REVNO)/rnr-server.tgz

files/r$(REVIEWS_REVNO)/rnr-server.tgz:
	@echo Creating tarball of code for deploy
	@mkdir -p files/r$(REVIEWS_REVNO)
	@tar czf $@ -C $(REVIEWS_CODE) .

upgrade-charm:
	juju upgrade-charm --repository=../.. ubuntu-reviews
