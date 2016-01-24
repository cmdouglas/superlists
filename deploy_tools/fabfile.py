from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/cmdouglas/superlists'

def deploy():
    site_folder = '/home/{user}/sites/{site_name}'.format(
        user=env.user,
        site_name=env.host
    )

    source_folder = site_folder + '/source'

    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_venv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'source'):
        run('mkdir -p {site_folder}/{subfolder}'.format(
            site_folder=site_folder,
            subfolder=subfolder
        ))

def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd {source_folder} && git fetch'.format(
            source_folder=source_folder
        ))
    else:
        run('git clone {REPO_URL} {source_folder}'.format(
            REPO_URL=REPO_URL,
            source_folder=source_folder
        ))

    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {source_folder} && git reset --hard {current_commit}'.format(
        source_folder=source_folder,
        current_commit=current_commit
    ))

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/superlists/settings.py'
    sed(settings_path, 'DEBUG = True', 'DEBUG = False')
    sed(
        settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["{site_name}"]'.format(site_name=site_name)
    )

    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, 'SECRET_KEY = "{key}"'.format(key=key))

    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_venv(source_folder):
    if not exists(source_folder + '/bin/pip'):
        run('python3 -m venv {source_folder}'.format(
            source_folder=source_folder
        ))
    run('{sf}/bin/pip install -r {sf}/requirements.txt'.format(
        sf=source_folder
    ))

def _update_static_files(source_folder):
    run('cd {sf} && ./bin/python3 manage.py collectstatic --noinput'.format(
        sf=source_folder
    ))

def _update_database(source_folder):
    run('cd {sf} && ./bin/python3 manage.py migrate --noinput'.format(
        sf=source_folder
    ))

