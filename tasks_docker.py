
"""
Tasks for smooth docking operations.
"""

from termcolor import cprint

from invoke import Collection, Failure, task, run
from invoke.util import cd


def big_fat_green(*args):
    cprint(' '.join(args), 'green', attrs=['bold'])


def build_tag_push(name, tag, directory='.', push=True):
    big_fat_green(' ===> Building', name)
    container_id = run('docker build ' + directory).stdout.rsplit(maxsplit=1)[-1]
    target_name = 'qabel/' + name
    if tag:
        target_name += ':' + tag
        big_fat_green(' ===> Tagging', container_id, 'as', target_name)
        run('docker tag {id} {tag}'.format(id=container_id, tag=target_name))
    if push:
        big_fat_green(' ===> Pushing', target_name)
        run('docker push ' + target_name)


@task(positional=['tag'])
def base(ctx, tag, push=True):
    """Build-tag-push base image. Requires tag name."""
    build_tag_push('base', tag, 'docker_base', push=push)


@task
def infra(ctx, tag='latest', push=True):
    """Build[-tag]-push infrastructure image. -t/--tag <tag>, default 'latest'."""
    build_tag_push('infrastructure', tag, push=push)


@task
def _run(ctx, tag='latest'):
    run('docker run -t -p 5000:5000/tcp -p 9696-9698:9696-9698 qabel/infrastructure:' + tag, pty=True)


@task
def clean(ctx):
    run('docker ps -aq | xargs docker rm', warn=True)
    run('docker images -q | xargs docker rmi', warn=True)


docker = Collection('docker')
docker.add_task(base)
docker.add_task(infra)
docker.add_task(_run, 'run')
docker.add_task(clean)
