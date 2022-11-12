# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import os
import urequests

APP_DIR = '/app'
OLD_DIR = '/old'
NEW_DIR = '/new'
VERSION_FILE = '.version'


def _github_latest_version(owner, repo, branch):
    response = urequests.get(
        'https://api.github.com/repos/{}/{}/branches/{}'.format(
            owner, repo, branch),
        headers={'User-Agent': 'micropython'})

    data = response.json()
    response.close()

    return data['commit']['sha']


def _local_latest_version():
    if VERSION_FILE in os.listdir(APP_DIR):
        with open('{}/{}'.format(APP_DIR, VERSION_FILE)) as f:
            return f.read()
    return None


def _rmdir(directory):
    try:
        for entry in os.ilistdir(directory):
            path = '{}/{}'.format(directory, entry[0])
            is_dir = entry[1] == 0x4000
            if is_dir:
                self._rmtdir(path)
            else:
                os.remove(path)
        os.rmdir(directory)
    except OSError:
        return


def check_for_update(owner, repo, branch='main') -> Bool:
    try:
        github_version = _github_latest_version(owner, repo, branch)
        local_version = _local_latest_version()

        return github_version != local_version
    except Exception as e:
        print('check_for_update error: {} {}'.format(type(e), e))
        return False


def install_update(owner, repo, branch='main'):
    import mip

    github_version = _github_latest_version(owner, repo, branch)

    # ensure cleanup
    _rmdir(OLD_DIR)
    _rmdir(NEW_DIR)

    # download
    print('Installing version {}'.format(github_version))
    mip.install('github:{}/{}'.format(owner, repo),
                target=NEW_DIR,
                version=github_version)

    with open('{}/{}'.format(NEW_DIR, VERSION_FILE), 'w') as f:
        f.write(github_version)

    # install
    os.rename(APP_DIR, OLD_DIR)
    os.rename(NEW_DIR, APP_DIR)
    _rmdir(OLD_DIR)
