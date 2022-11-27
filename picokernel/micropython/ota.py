# Copyright (c) 2022 Richard Titmuss
#
# SPDX-License-Identifier: MIT

import os
import urequests

VERSION_FILE = '.version'


def _github_latest_version(owner, repo, branch):
    response = urequests.get(
        'https://api.github.com/repos/{}/{}/branches/{}'.format(
            owner,
            repo.split('/', 1)[0], branch),
        headers={'User-Agent': 'micropython'})

    data = response.json()
    response.close()

    return data['commit']['sha']


def _local_latest_version(target):
    if VERSION_FILE in os.listdir(target):
        with open('{}/{}'.format(target, VERSION_FILE)) as f:
            return f.read()
    return None


def _rmdir(directory):
    try:
        for entry in os.ilistdir(directory):
            path = '{}/{}'.format(directory, entry[0])
            is_dir = entry[1] == 0x4000
            if is_dir:
                _rmdir(path)
            else:
                os.remove(path)
        os.rmdir(directory)
    except OSError:
        return


def check_for_update(owner, repo, target, branch='main') -> Bool:
    try:
        github_version = _github_latest_version(owner, repo, branch)
        local_version = _local_latest_version(target)

        return github_version != local_version
    except Exception as e:
        print('check_for_update error: {} {}'.format(type(e), e))
        return False


def install_update(owner, repo, target, branch='main'):
    import mip

    github_version = _github_latest_version(owner, repo, branch)

    old_dir = '{}.old'.format(target)
    new_dir = '{}.new'.format(target)

    # ensure cleanup
    _rmdir(old_dir)
    _rmdir(new_dir)

    # download
    print('Installing version {}'.format(github_version))
    mip.install('github:{}/{}'.format(owner, repo),
                target=new_dir,
                version=github_version)

    with open('{}/{}'.format(new_dir, VERSION_FILE), 'w') as f:
        f.write(github_version)

    # install
    os.rename(target, old_dir)
    os.rename(new_dir, target)
    _rmdir(old_dir)
