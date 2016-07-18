
"""
Tasks for managing ad-hoc PostgreSQL and Redis instances for testing purposes.
"""

import os
import shutil
import signal
import time
from pathlib import Path

from invoke import Collection, Failure, task, run

PGSQL_SUFFIX = 27901

PGSQL_NAMES = [
    'qabel-block',
    'qabel-accounting',
    'qabel-drop',
    'qabel-index',
]

REDIS_PORT = 27902


def kill_pidfile(path, signo=signal.SIGTERM, unlink=True):
    try:
        with path.open() as pidfile:
            pid = int(pidfile.read())
    except FileNotFoundError:
        print('{} doesn\'t exist; {} is not running.'.format(path, path.stem))
        return
    print('Waiting for {} to die ...'.format(path.stem), end='')
    while True:
        try:
            os.kill(pid, signo)
        except OSError:
            break
        print('.', end='')
        time.sleep(.1)
    if unlink:
        path.unlink()
    print()


def pidfile_alive(path):
    try:
        with path.open() as pidfile:
            pid = int(pidfile.read())
    except FileNotFoundError:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def create_user_db(name, ignore_errors=True):
    """Create user and database with *name*."""
    hide = 'both' if ignore_errors else None
    try:
        run('createuser -p {suffix} -h /tmp {name}'.format(suffix=PGSQL_SUFFIX, name=name), hide=hide)
        run('createdb -p {suffix} -h /tmp {name}'.format(suffix=PGSQL_SUFFIX, name=name), hide=hide)
    except Failure:
        if not ignore_errors:
            raise


@task(name='postgres')
def start_postgres(ctx):
    # pg_ctl(1)
    # If the server is not running, the process returns an exit status of 3.
    NOT_RUNNING = 3

    pgsql_path = Path(ctx.qabel.testing.app_data) / 'postgres'
    pgsql_path.parent.mkdir(exist_ok=True, parents=True)
    pg_ctl = ctx.qabel.testing.pgctl

    first_time = not pgsql_path.exists()
    if first_time:
        run('{pg_ctl} init -D {}'.format(pgsql_path, pg_ctl=pg_ctl))
    try:
        run('{pg_ctl} status -D {}'.format(pgsql_path, pg_ctl=pg_ctl))
    except Failure as failure:  # failure is not an option

        if failure.result.return_code != NOT_RUNNING:
            raise

        # Not runnning, let's get it up
        run('{pg_ctl} start -D {path} -o "-p {suffix} -c log_destination=stderr -c unix_socket_directories=/tmp"'
            .format(path=pgsql_path, suffix=PGSQL_SUFFIX, pg_ctl=pg_ctl))

        # Wait for postgres to start up
        while True:
            try:
                run('{pg_ctl} status -D {}'.format(pgsql_path, pg_ctl=pg_ctl))
                time.sleep(1)
            except Failure as failure:
                if failure.result.return_code != NOT_RUNNING:
                    raise
            else:
                break

        # Try to create user + DB
        for name in PGSQL_NAMES:
            create_user_db(name, ignore_errors=not first_time)


@task(name='redis')
def start_redis(ctx):
    app_data = Path(ctx.qabel.testing.app_data)
    redis_path = app_data / 'redis'
    redis_pidfile = app_data / 'redis.pid'
    redis_server = ctx.qabel.testing.redis
    command_line = [
        redis_server,
        '--bind', 'localhost',
        '--port', REDIS_PORT,
        '--pidfile', redis_pidfile.absolute(),
        '--dir', redis_path,
        '&'
    ]
    redis_path.mkdir(exist_ok=True, parents=True)
    run(' '.join(map(str, command_line)))


@task(pre=[start_postgres, start_redis])
def start_all(ctx):
    """
    Start PostgreSQL and Redis servers.

    Meant for development and testing purposes, not production use.
    """


start_servers = Collection('start')
start_servers.add_task(start_all, default=True)
start_servers.add_task(start_postgres)
start_servers.add_task(start_redis)


@task(name='postgres')
def stop_postgres(ctx):
    pgsql_path = Path(ctx.qabel.testing.app_data) / 'postgres'
    pg_ctl = ctx.qabel.testing.pgctl
    if not pgsql_path.exists():
        return
    run('{pg_ctl} stop -D {}'.format(pgsql_path, pg_ctl=pg_ctl), warn=True)


@task(name='redis')
def stop_redis(ctx):
    app_data = Path(ctx.qabel.testing.app_data)
    redis_pidfile = app_data / 'redis.pid'
    kill_pidfile(redis_pidfile, unlink=False)


@task(pre=[stop_postgres, stop_redis])
def stop_all(ctx):
    """
    Stop PostgreSQL and Redis servers.
    """


@task(pre=[stop_all])
def clean_all(ctx):
    def clean(path):
        try:
            shutil.rmtree(str(path))
        except OSError as e:
            print('clean', path, e)

    app_data = Path(ctx.qabel.testing.app_data)

    clean(app_data / 'postgres')
    clean(app_data / 'redis')


@task
def status(ctx):
    app_data = Path(ctx.qabel.testing.app_data)
    redis_pidfile = app_data / 'redis.pid'
    if pidfile_alive(redis_pidfile):
        print('redis is started, PID', redis_pidfile.read_text().strip())
    else:
        print('redis is stopped')

    pgsql_path = app_data / 'postgres'
    pg_ctl = ctx.qabel.testing.pgctl
    if not pgsql_path.exists():
        print('postgres is not initialized')
        return
    run('{pg_ctl} status -D {}'.format(pgsql_path, pg_ctl=pg_ctl), warn=True)


stop_servers = Collection('stop')
stop_servers.add_task(stop_all, default=True)
stop_servers.add_task(stop_postgres)
stop_servers.add_task(stop_redis)

servers = Collection('servers')
servers.add_collection(start_servers)
servers.add_collection(stop_servers)
servers.add_task(clean_all, 'clean')
servers.add_task(status, 'status')
