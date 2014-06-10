charm-bootstrap-wsgi
====================

This repo is a template charm for any [juju][1] deployed wsgi service.
As is, this charm deploys an example wsgi service with nagios checks and simple
rolling upgrades.

You can re-use this charm to deploy any wsgi service by updating the
playbook.yaml file. All of the wsgi functionality is provided
by a reusable wsgi-app ansible role (see roles/wsgi-app) together
with the gunicorn charm.

Disclaimer: this template does not try to explain what's possible with
either ansible or juju - but if you know a bit about both, it will
show you how you can easily use them together.


## Deploying the charm

Make sure you've got a bootstrapped juju environment ready, and then:

```
$ mkdir -p ~/charms/precise && cd ~/charms/precise
$ git clone https://github.com/absoludity/charm-bootstrap-wsgi
$ cd charm-bootstrap-wsgi
$ make deploy
```

You should now be able to curl your service to see it working:

```
$ make curl
juju run --service wsgi-example "curl -s http://localhost:8080"
- MachineId: "1"
  Stdout: 'It works! Revision 1'
  UnitId: charm-bootstrap-wsgi/0
- MachineId: "2"
  Stdout: 'It works! Revision 1'
  UnitId: charm-bootstrap-wsgi/1
```

You can also see the output of all the configured nagios checks,
including the check_http added by the playbook, by running:
```
$ make nagios
```

## Your custom deployment code

To deploy your own custom wsgi application, open up the playbook.yml
In addition to the wsgi-app reusable role and the optional nagios reusable role
(nrpe-external-master), it only has two tasks:

 * installing any package dependencies
 * Re-rendering the app's config file (and triggering a wsgi restart)

If you find yourself needing to do more than this, let me know :-)

For simplicity, the default example app is deployed from the charm itself with
the archived code in the charm's files directory. But the wsgi-app role also
allows you to define a code_assets_uri, which if set, will be used instead of
the charm's files directory.

The nagios check used for your app can be updated by adjusting the
check_params passed to the role in playbook.yml (or you can additionally
add further nagios checks depending on your needs).


## A rolling upgrade example

Assuming you've already deployed the example service, we first update
the configuration so that the units continue to run the 'r1' build
(current_symlink), while simultaneously ensuring that the 'r2' build
is installed and ready to run:
```
$ juju set wsgi-example current_symlink=r1 build_label=r2
```

Next, manually set just one unit to use the r2 build:

```
$ juju run --unit wsgi-example/0 "CURRENT_SYMLINK=r2 actions/set-current-symlink"

PLAY [localhost] **************************************************************

GATHERING FACTS ***************************************************************
ok: [localhost]

TASK: [wsgi-app | Manually set current symlink.] ******************************
changed: [localhost]

NOTIFIED: [wsgi-app | Restart wsgi] *******************************************
changed: ...

PLAY RECAP ********************************************************************
localhost                  : ok=3    changed=2    unreachable=0    failed=0
```

Verify that the new revision is working correctly on the one instance:

```
$ make curl
juju run --service wsgi-example "curl -s http://localhost:8080"
- MachineId: "1"
  Stdout: 'It works! Revision 2'
  UnitId: wsgi-example/0
- MachineId: "2"
  Stdout: 'It works! Revision 1'
  UnitId: wsgi-example/1
```

Update any others, or when you're confident, update the full set with:

```
$ juju set wsgi-example current_symlink=r2
```

and then verify that all units are service the latest with `make curl` again.


### Note about test Dependencies
The makefile to run tests requires the following dependencies

- python-nose
- python-mock
- python-flake8

installable via:

```
$ sudo apt-get install python-nose python-mock python-flake8
```

[1]: http://juju.ubuntu.com/
[2]: http://ansibleworks.com/
