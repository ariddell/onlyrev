"""fabfile for deploying django projects.

Needs ``fabric_settings.py``. See ``fabric_settings.py.example``.

Needs as well ``projectname/local_settings_production.py``. See 
``projectname/local_settings_production.py.example``

Assumes virtualenvwrapper is installed remotely and something close to the
following appears in .bashrc on the remote server:

    export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python2.7
    export WORKON_HOME=${HOME}/.virtualenvs
    source ${HOME}/bin/virtualenvwrapper.sh
    export PIP_VIRTUALENV_BASE=$WORKON_HOME
    export PIP_RESPECT_VIRTUALENV=true

Draws from ``webfaction-django-boilerplate``
"""

from fabric.api import (
    cd,
    env,
    lcd,
    local,
    run,
    settings,
)
from fabric.contrib.files import sed

import fabric_settings as fab_settings

env.hosts = fab_settings.ENV_HOSTS
env.user = fab_settings.ENV_USER
env.project_name = fab_settings.PROJECT_NAME

###############################################################################
# HIGH LEVEL TASKS
###############################################################################

def install_all():
    install_server()
    local_link_repo_with_remote_repo()
    first_deployment()

def install_server():
    run_install_virtualenv()
    run_create_git_repo()
    run_delete_index_files()

def first_deployment():
    run_delete_previous_attempts()
    run_create_project_virtualenv()
    run_create_project_repo()
    run_install_requirements()
    run_deploy_website(syncdb=False)
    run_copy_local_settings()
    run_setup_apache()
    run_deploy_website(syncdb=True)

def deploy(syncdb=False):
    """To deploy and run syncdb, collectstatic use the following fabric
    command: ``fab deploy:syncdb=True``"""
    run_deploy_website(syncdb)

###############################################################################
# LOCAL TASKS
###############################################################################

def local_link_repo_with_remote_repo():
    with lcd(fab_settings.PROJECT_ROOT):
        local('git config http.sslVerify false')
        local('git config http.postBuffer 524288000')
        with settings(warn_only=True):
            local('git remote rm origin')
        local('git remote add origin'
              ' {0}@{0}.webfactional.com:'
              '/home/{0}/webapps/git/repos/{1}'.format(
                    fab_settings.ENV_USER, fab_settings.GIT_REPO_NAME))
        local('git push -u origin master')

def run_copy_local_settings():
    with lcd(fab_settings.PROJECT_ROOT):
        local('scp {0}/local_settings_production.py {1}@{1}.webfactional.com:'
              '/home/{1}/webapps/{2}/myproject/{0}/local_settings.py'.format(
                                                 fab_settings.PROJECT_NAME,
                                                 fab_settings.ENV_USER,
                                                 fab_settings.DJANGO_APP_NAME))
def run_setup_apache():
    with cd('$HOME/webapps/{0}/apache2/conf/'.format(
                                                fab_settings.DJANGO_APP_NAME)):
        sed('httpd.conf', 'myproject/wsgi.py', '{0}/wsgi.py'.format(
                                                fab_settings.PROJECT_NAME))

###############################################################################
# REMOTE TASKS
###############################################################################

def run_install_virtualenv():
    with cd('$HOME'):
        run('mkdir -p $HOME/lib/python2.7')
        run('easy_install-2.7 virtualenv')
        run('easy_install-2.7 pip')
        run('pip install virtualenvwrapper')
        run('mkdir -p $HOME/.virtualenvs')

def run_create_git_repo():
    run('rm -rf $HOME/webapps/git/repos/{0}'.format(
        fab_settings.GIT_REPO_NAME))
    with cd('$HOME/webapps/git'):
        run('git init --bare ./repos/{0}'.format(fab_settings.GIT_REPO_NAME))
    with cd('$HOME/webapps/git/repos/{0}'.format(fab_settings.GIT_REPO_NAME)):
        run('git config http.receivepack true')

def run_delete_index_files():
    run('rm -f $HOME/webapps/{0}/index.html'.format(
        fab_settings.MEDIA_APP_NAME))
    run('rm -f $HOME/webapps/{0}/index.html'.format(
        fab_settings.STATIC_APP_NAME))

def run_delete_previous_attempts():
    run('rm -rf $HOME/webapps/{0}/myproject'.format(
        fab_settings.DJANGO_APP_NAME))
    run('rm -rf $HOME/.virtualenvs/{0}/'.format(fab_settings.VENV_NAME))

def run_create_project_virtualenv():
    with cd('$HOME'):
        run('rm -rf $HOME/.virtualenvs/{0}'.format(fab_settings.VENV_NAME))
        run('mkvirtualenv -p python2.7 --system-site-packages {0}'.format(
            fab_settings.VENV_NAME))

def run_create_project_repo():
    with cd('$HOME/webapps/{0}'.format(fab_settings.DJANGO_APP_NAME)):
        run('git clone $HOME/webapps/git/repos/{0} myproject'.format(
            fab_settings.GIT_REPO_NAME))

def run_install_requirements():
    run('workon {0} && pip install -r $HOME/webapps/{1}/myproject/'
        'requirements.txt --upgrade'.format(fab_settings.VENV_NAME,
                           fab_settings.DJANGO_APP_NAME))

def run_deploy_website(syncdb=False):
    with cd('$HOME/webapps/{0}/myproject'.format(fab_settings.DJANGO_APP_NAME)):
        run('git pull origin master')
        if syncdb:
            run('workon {0} && ./manage.py syncdb --noinput'.format(
                fab_settings.VENV_NAME))
            run('workon {0} && ./manage.py collectstatic --noinput'.format(
                fab_settings.VENV_NAME))
            run('$HOME/webapps/{0}/apache2/bin/restart'.format(
                                                 fab_settings.DJANGO_APP_NAME))
