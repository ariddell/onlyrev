import os
from fabric.api import *
from fabric.contrib import console
from fabric import utils

import fabric_settings as fab_settings

env.git_repo = fab_settings.GIT_REPO
env.project = fab_settings.PROJECT_NAME
env.virtualenv_root = os.path.join("~/.virtualenvs/", env.project)

def production():
    """Use production environment on remote host"""
    env.environment = 'production'
    env.hosts = fab_settings.ENV_HOSTS
    env.root = os.path.join("~/webapps/", env.project)
    env.code_root = os.path.join(env.root, env.project)

def bootstrap():
    """Initialize remote host environment (virtualenv, deploy, update)"""
    require('root', provided_by=('production'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to bootstrap production?',
                               default=False):
            utils.abort('Production bootstrapping aborted.')
    create_virtualenv()
    run('mkdir -p %(root)s' % env)
    with cd(env.root):
        run('git init')
        run('git remote add origin %(git_repo)s' % env)
        run('git config branch.master.remote origin')
        run('git config branch.master.merge refs/heads/master')
        run('git pull')
    update_requirements()
    deploy()

def create_virtualenv():
    """Setup virtualenv on remote host."""
    require('virtualenv_root', provided_by=('production'))
    args = '--clear --no-site-packages --distribute --python=python2.7'
    run('virtualenv %s %s' % (args, env.virtualenv_root))

def deploy():
    """Checkout git repository to remote host."""
    require('root', 'code_root', provided_by=('production'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy production?',
                               default=False):
            utils.abort('Production deployment aborted.')
    with cd('%(root)s' % env):
        run('git pull')
        run('workon %(project)s ; ./manage.py syncdb --noinput' % env)
        run('workon %(project)s ; ./manage.py collectstatic --noinput' % env)
    with cd(os.path.join(env.root, 'apache2/bin/')):
        run('./restart')

def update_requirements():
    """Update external dependencies on remote host."""
    require('code_root', provided_by=('production'))
    with cd(env.root):
        run('workon %(project)s && pip install -r requirements.txt '
            '--upgrade' % env)

def stop():
    """Stop apache."""
    require('root', 'code_root', provided_by=('production'))
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to stop production?',
                               default=False):
            utils.abort('Production deployment aborted.')
    with cd(os.path.join(env.root, 'apache2/bin/')):
        run('./stop')
