# qabel-infrastructure

## Ad-hoc deployment/testing

#### You'll need

* PostgreSQL 9.5+ (does not need to be started, a running instance will not be used)
  * + libraries (for building psycopg2)
* Redis (does not need to be started, a running instance will not be used)
* Python 3.5
  * + virtualenv

#### Setup

    $ ./bootstrap.sh
    Run '. ./activate.sh' to activate this environment.
    $ . ./activate.sh
    See 'inv --list' for available tasks.
    $ # Get fresh code (do this after one of the downstream repos was updated)
    $ inv update

Note: `app-data` can't be a VirtualBox shared directory.


    $ cat invoke.yaml
    qabel:
        testing:
            app_data: /tmp/qabel-testing-app-data

Or anywhere else where there's a normal FS. Note that the Qabel application servers
still store their data under `app-data` by default (e.g. `qabel.block.local-storage`),
which is not a problem, not even for VirtualBox shared directories :)

#### Running the platform test suite

    $ # Run some tests
    $ inv test

This starts the necessary ancillary servers (postgres, redis) and the uWSGI instance
running our services/applications.

For debugging -p/--pytest-args specifies additional arguments to pass to py.test,
e.g. --pdb, like so:

    $ inv test -p '--pdb'

Additional test environments can be defined, not just ones started by these scripts.
The test environment is select by -w/--which. The default is adhoc.

#### Faster test cycles

When developing tests or debugging tests, test time can be reduced considerably
by starting the servers separately (`inv start`) from running the tests (`inv test`,
which will detect if the servers are already running and won't start or stop them then).

A further reduction can be achieved by running `py.test` directly. Copy the printed command
line and just use that. If you use the default test environment you can just call `py.test`
with no extra arguments, the defaults are the same :)

Note that running `py.test` directly doesn't re-deploy the servers, so any changes in
code or configuration won't be reflected.

#### Starting a testing configuration

(which **should be** compatible with `start-servers.sh`)

    $ inv start

(Exit via ^C/Ctrl-C -- or `inv start --background`, and then `inv stop`)

#### Reference:

    $ inv --list
    Available tasks:

      deploy
      start                                     Run server with uWSGI.
      status
      stop
      test                                      Run the test suite against ad-hoc created infrastructure.
      update                                    Update applications/* from git origin.
      servers.clean
      servers.status
      servers.start.postgres
      servers.start.redis
      servers.start.start_all (servers.start)   Start PostgreSQL and Redis servers.
      servers.stop.postgres
      servers.stop.redis
      servers.stop.stop_all (servers.stop)      Stop PostgreSQL and Redis servers.


    # Also see inv --help <task name> (yeah I know it should be <task name> --help)

